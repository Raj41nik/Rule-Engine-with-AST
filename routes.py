import re
from flask import request
from flask_restful import Resource
from models import Rule, db
from lark import Lark, Transformer, v_args

# Updated grammar to accept both single and double-quoted strings
grammar = """
    ?start: expr

    ?expr: expr "OR" term   -> or_expr
         | expr "AND" term  -> and_expr
         | term

    ?term: "NOT" term       -> not_expr
         | "(" expr ")"
         | comparison

    ?comparison: NAME OPERATOR value

    OPERATOR: ">" | "<" | "=" | ">=" | "<="

    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/

    ?value: SIGNED_NUMBER   -> number
          | STRING          -> string

    // Updated STRING definition to accept both single and double-quoted strings
    STRING : /"([^"\\\\]|\\\\.)*"|'([^'\\\\]|\\\\.)*'/

    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
"""

# Define a Node class for the AST
class Node:
    def __init__(self, type, value=None, left=None, right=None, negate=False):
        self.type = type  # "operator" or "operand"
        self.value = value  # Operator or operand details
        self.left = left
        self.right = right
        self.negate = negate  # For handling NOT operators

    def __repr__(self):
        return f"Node(type={self.type}, value={self.value}, left={self.left}, right={self.right}, negate={self.negate})"

@v_args(inline=True)
class ASTTransformer(Transformer):
    def start(self, expr):
        return expr

    def or_expr(self, left, right):
        return Node(type="operator", value="OR", left=left, right=right)

    def and_expr(self, left, right):
        return Node(type="operator", value="AND", left=left, right=right)

    def not_expr(self, node):
        # Apply negation to the node
        node.negate = not node.negate
        return node

    def comparison(self, field, operator, value):
        return Node(type="operand", value=(str(field), str(operator), value))

    def number(self, token):
        return int(token)

    def string(self, token):
        # Remove the surrounding quotes from the string
        return token[1:-1]

    def NAME(self, token):
        return str(token)

    def OPERATOR(self, token):
        return str(token)

class CreateRule(Resource):
    def post(self):
        try:
            # Get the rule string from the request body
            data = request.get_json()
            rule_string = data.get('rule')

            if not rule_string:
                return {"message": "No rule string provided"}, 400

            # Parse the rule and generate AST
            ast = self.parse_rule(rule_string)

            # Return the AST as a JSON object
            return {"message": "Rule created successfully", "AST": self.serialize_ast(ast)}, 200
        except Exception as e:
            return {"message": f"Error creating rule: {str(e)}"}, 500

    def parse_rule(self, rule_string):
        parser = Lark(grammar, start='start', parser='lalr')
        transformer = ASTTransformer()
        parse_tree = parser.parse(rule_string)
        ast = transformer.transform(parse_tree)
        return ast

    def serialize_ast(self, node):
        if node is None:
            return None
        ast_node = {
            "type": node.type,
            "value": node.value,
            "negate": node.negate
        }
        children = []
        if node.left:
            left_serialized = self.serialize_ast(node.left)
            if left_serialized is not None:
                children.append(left_serialized)
        if node.right:
            right_serialized = self.serialize_ast(node.right)
            if right_serialized is not None:
                children.append(right_serialized)
        if children:
            ast_node["children"] = children
        return ast_node

class EvaluateRule(Resource):
    def post(self):
        try:
            # Get the AST and user data from the request body
            data = request.get_json()
            ast = data.get('AST')  # Expecting an AST object
            user_data = data.get('user_data')

            if not ast or not user_data:
                return {"message": "Missing AST or user data"}, 400

            # Deserialize the AST
            ast_node = self.deserialize_ast(ast)
            result = self.evaluate_ast(ast_node, user_data)

            return {"message": "Rule evaluated", "result": result}, 200
        except Exception as e:
            return {"message": f"Error evaluating rule: {str(e)}"}, 500

    def evaluate_ast(self, node, user_data):
        if node.type == "operator":
            left_result = self.evaluate_ast(node.left, user_data)
            right_result = self.evaluate_ast(node.right, user_data)
            if node.value == "AND":
                result = left_result and right_result
            elif node.value == "OR":
                result = left_result or right_result
            else:
                result = False
        elif node.type == "operand":
            field, operator, value = node.value
            user_value = user_data.get(field)
            if user_value is None:
                result = False
            else:
                if operator == ">":
                    result = user_value > value
                elif operator == "<":
                    result = user_value < value
                elif operator == "=":
                    result = user_value == value
                elif operator == ">=":
                    result = user_value >= value
                elif operator == "<=":
                    result = user_value <= value
                else:
                    result = False
        else:
            result = False

        # Apply negation if needed
        if node.negate:
            return not result
        else:
            return result

    def deserialize_ast(self, node_data):
        if node_data is None:
            return None
        node = Node(
            type=node_data["type"],
            value=node_data["value"],
            negate=node_data["negate"]
        )
        children = node_data.get("children", [])
        if children:
            node.left = self.deserialize_ast(children[0]) if len(children) > 0 else None
            node.right = self.deserialize_ast(children[1]) if len(children) > 1 else None
        return node

class CombineRules(Resource):
    def post(self):
        try:
            data = request.get_json()
            rule_strings = data.get('rules')  # List of rule strings to combine

            if not rule_strings or len(rule_strings) < 2:
                return {"message": "At least two rules are required for combination"}, 400

            parser = Lark(grammar, start='start', parser='lalr')
            transformer = ASTTransformer()

            asts = []
            for rule_string in rule_strings:
                parse_tree = parser.parse(rule_string)
                ast = transformer.transform(parse_tree)
                asts.append(ast)

            # Combine ASTs using AND or OR
            combined_ast = asts[0]
            for ast in asts[1:]:
                combined_ast = Node(
                    type="operator",
                    value="AND",  # Change to "OR" if desired
                    left=combined_ast,
                    right=ast
                )

            return {"message": "Rules combined successfully", "AST": self.serialize_ast(combined_ast)}, 200
        except Exception as e:
            return {"message": f"Error combining rules: {str(e)}"}, 500

    def serialize_ast(self, node):
        # Reuse the serialize_ast method from CreateRule
        if node is None:
            return None
        ast_node = {
            "type": node.type,
            "value": node.value,
            "negate": node.negate
        }
        children = []
        if node.left:
            left_serialized = self.serialize_ast(node.left)
            if left_serialized is not None:
                children.append(left_serialized)
        if node.right:
            right_serialized = self.serialize_ast(node.right)
            if right_serialized is not None:
                children.append(right_serialized)
        if children:
            ast_node["children"] = children
        return ast_node

class ModifyRule(Resource):
    def post(self):
        try:
            # Get the AST, modification details from the request body
            data = request.get_json()
            ast = data.get('AST')  # The existing rule AST
            modification = data.get('modification')  # Details about what to modify

            if not ast or not modification:
                return {"message": "Missing AST or modification details"}, 400

            # Deserialize the AST from the JSON format into Node objects
            ast_node = self.deserialize_ast(ast)

            # Apply modifications to the AST based on the provided modification
            modified_ast = self.modify_ast(ast_node, modification)

            return {"message": "Rule modified successfully", "AST": self.serialize_ast(modified_ast)}, 200
        except Exception as e:
            return {"message": f"Error modifying rule: {str(e)}"}, 500


    def modify_ast(self, ast_node, modification):
        if modification['action'] == 'add_condition':
            new_condition = Node(
                type="operand",
                value=(modification['field'], modification['operator'], modification['value'])
            )
            return Node(
                type="operator",
                value="AND",
                left=ast_node,
                right=new_condition
            )
        elif modification['action'] == 'remove_condition':
            if ast_node.type == "operator":
                if self.condition_matches(ast_node.left, modification['field'], modification['operator'], modification['value']):
                    return ast_node.right
                elif self.condition_matches(ast_node.right, modification['field'], modification['operator'], modification['value']):
                    return ast_node.left
            return ast_node
        elif modification['action'] == 'change_operator':
            ast_node.value = modification['new_operator']
            return ast_node

        return ast_node

    def condition_matches(self, node, field, operator, value):
        if node.type == "operand":
            return node.value == (field, operator, value)
        return False

    def deserialize_ast(self, node_data):
        if node_data is None:
            return None
        node = Node(
            type=node_data["type"],
            value=node_data["value"],
            negate=node_data["negate"]
        )
        children = node_data.get("children", [])
        if children:
            node.left = self.deserialize_ast(children[0]) if len(children) > 0 else None
            node.right = self.deserialize_ast(children[1]) if len(children) > 1 else None
        return node

    def serialize_ast(self, node):
        # Reuse the serialize_ast method
        if node is None:
            return None
        ast_node = {
            "type": node.type,
            "value": node.value,
            "negate": node.negate
        }
        children = []
        if node.left:
            left_serialized = self.serialize_ast(node.left)
            if left_serialized is not None:
                children.append(left_serialized)
        if node.right:
            right_serialized = self.serialize_ast(node.right)
            if right_serialized is not None:
                children.append(right_serialized)
        if children:
            ast_node["children"] = children
        return ast_node

class StoreRule(Resource):
    def post(self):
        try:
            # Get the rule string and AST from the request body
            data = request.get_json()
            rule_string = data.get('rule_string')
            ast = data.get('AST')

            if not rule_string or not ast:
                return {"message": "Missing rule_string or AST"}, 400

            # Store the rule in the database
            rule = Rule(rule_string=rule_string, ast=ast)
            db.session.add(rule)
            db.session.commit()

            return {"message": "Rule stored successfully", "rule_id": rule.id}, 200
        except Exception as e:
            return {"message": f"Error storing rule: {str(e)}"}, 500

class GetRule(Resource):
    def get(self, rule_id):
        try:
            # Retrieve the rule by its ID
            rule = Rule.query.get(rule_id)

            if not rule:
                return {"message": "Rule not found"}, 404

            return {"rule_string": rule.rule_string, "AST": rule.ast}, 200
        except Exception as e:
            return {"message": f"Error retrieving rule: {str(e)}"}, 500

class ListRules(Resource):
    def get(self):
        try:
            # List all rules in the database
            rules = Rule.query.all()
            rule_list = [{"id": rule.id, "rule_string": rule.rule_string, "AST": rule.ast} for rule in rules]

            return {"rules": rule_list}, 200
        except Exception as e:
            return {"message": f"Error listing rules: {str(e)}"}, 500

# This function initializes the routes for the API
def initialize_routes(api):
    api.add_resource(CreateRule, "/api/create_rule")
    api.add_resource(EvaluateRule, "/api/evaluate_rule")
    api.add_resource(CombineRules, "/api/combine_rules")
    api.add_resource(ModifyRule, "/api/modify_rule")
    api.add_resource(StoreRule, "/api/store_rule")
    api.add_resource(GetRule, "/api/get_rule/<int:rule_id>")
    api.add_resource(ListRules, "/api/list_rules")
