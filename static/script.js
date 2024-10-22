// Global variables to store the current AST and rule string
window.currentAST = null;
window.currentRuleString = null;

// Function to create the rule and display AST
document.getElementById("create-rule-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const rule = document.getElementById("rule").value;

    fetch("/api/create_rule", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ rule: rule })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Rule created successfully") {
            console.log("Generated AST:", data.AST);
            // Store the AST and rule string globally
            window.currentAST = data.AST;
            window.currentRuleString = rule;
            // Call the function to render the AST using D3
            renderAstTree(data.AST);
        } else {
            alert("Error creating rule: " + data.message);
        }
    })
    .catch(err => {
        console.error("Error:", err);
    });
});

// Function to evaluate the rule with user data
document.getElementById("evaluate-rule-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const userDataText = document.getElementById("user-data").value;
    let userData;

    try {
        userData = JSON.parse(userDataText);
    } catch (err) {
        alert("Invalid JSON format in user data.");
        return;
    }

    if (!window.currentAST) {
        alert("No AST available. Please create a rule first.");
        return;
    }

    fetch("/api/evaluate_rule", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ AST: window.currentAST, user_data: userData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Rule evaluated") {
            alert("Rule evaluation result: " + data.result);
        } else {
            alert("Error evaluating rule: " + data.message);
        }
    })
    .catch(err => {
        console.error("Error:", err);
    });
});

// Function to modify the current rule
document.getElementById("modify-rule-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const modificationText = document.getElementById("modification").value;
    let modification;

    try {
        modification = JSON.parse(modificationText);
    } catch (err) {
        alert("Invalid JSON format in modification.");
        return;
    }

    if (!window.currentAST) {
        alert("No AST available. Please create a rule first.");
        return;
    }

    fetch("/api/modify_rule", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ AST: window.currentAST, modification: modification })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Rule modified successfully") {
            console.log("Modified AST:", data.AST);
            // Update the current AST
            window.currentAST = data.AST;
            // Re-render the AST
            renderAstTree(data.AST);
            alert("Rule modified successfully.");
        } else {
            alert("Error modifying rule: " + data.message);
        }
    })
    .catch(err => {
        console.error("Error:", err);
    });
});

// Function to store the current rule
document.getElementById("store-rule-form").addEventListener("submit", function (e) {
    e.preventDefault();

    if (!window.currentRuleString || !window.currentAST) {
        alert("No rule available to store. Please create a rule first.");
        return;
    }

    fetch("/api/store_rule", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ rule_string: window.currentRuleString, AST: window.currentAST })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Rule stored successfully") {
            alert("Rule stored with ID: " + data.rule_id);
        } else {
            alert("Error storing rule: " + data.message);
        }
    })
    .catch(err => {
        console.error("Error:", err);
    });
});

// Function to render AST using D3.js with a vertical layout
function renderAstTree(astData) {
    // Clear any previous tree
    document.getElementById('ast-tree').innerHTML = '';

    const width = 600;
    const height = 500;

    // Create the SVG container
    const svg = d3.select("#ast-tree").append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(50,50)");

    // Convert the AST into a hierarchy that D3 can understand
    const root = d3.hierarchy(astData);

    // Apply a tree layout
    const treeLayout = d3.tree().size([height - 100, width - 100]);
    treeLayout(root);

    // Draw links (lines between nodes)
    svg.selectAll(".link")
        .data(root.links())
        .enter()
        .append("path")
        .attr("class", "link")
        .attr("fill", "none")
        .attr("stroke", "#ccc")
        .attr("stroke-width", 2)
        .attr("d", d3.linkHorizontal()
            .x(d => d.y)
            .y(d => d.x)
        );

    // Draw nodes (circles and labels)
    const node = svg.selectAll(".node")
        .data(root.descendants())
        .enter()
        .append("g")
        .attr("class", "node")
        .attr("transform", d => `translate(${d.y},${d.x})`);

    // Add circles to represent nodes
    node.append("circle")
        .attr("r", 5)
        .attr("fill", "steelblue");

    // Add text labels for each node
    node.append("text")
        .attr("dy", 3)
        .attr("x", d => d.children ? -10 : 10)
        .style("text-anchor", d => d.children ? "end" : "start")
        .text(d => {
            if (d.data.type === "operand" && d.data.value) {
                const [field, operator, value] = d.data.value;
                return `${field} ${operator} ${value}`;
            } else if (d.data.type === "operator") {
                return d.data.value;
            } else {
                return 'Unknown';
            }
        });
}

