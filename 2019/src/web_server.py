from cli import TreeShell
from flask import Flask, Markup, render_template, request, redirect, url_for
import sys
from truthtrees import pretty_print
import io

app = Flask(__name__)

log = io.StringIO()

shell = TreeShell(stdout=log)

closed_string = "<span style='color: red;'>X</span>"
open_string = "<span style='color: green;'>O</span>"


@app.route('/', methods=['POST', 'GET'])
def my_form():
    """
    This is the function:
    * calls a shell command(s) based on the inputs and
    * render nodes, formulas, and the tree to be displayed in html
    * reloads the page with the updates
    """
    if request.method == 'GET':
        shell.stdout.write(str(shell.intro)+"\n")
        log = shell.stdout.getvalue().split('\n')
        return render_template('my-form.html', log=log, command_history=shell.history)
    elif request.method == 'POST':
        text = request.form.get('text')
        reset = request.form.get('reset')
        verify = request.form.get('verify')
        if reset:
            shell.onecmd("reset")
            log = shell.stdout.getvalue().split('\n')
            tree_render = render_node(shell.tree.root, shell.current_node.node_id)
            return render_template('my-form.html', command_history=shell.history, log=log, tree=tree_render)
        elif verify:
            closed_verify = shell.onecmd("check_all_closed")
            open_verify = shell.onecmd("check_any_open")
            if closed_verify == "True" or open_verify == "True":
                verify_message = "Verified Success!"
                verify_render = Markup(render_template("verify_success.html", verify_message=verify_message))
            elif closed_verify == "False" and open_verify == "False":
                verify_message = "Verified Failed. Check the Log"
                verify_render = Markup(render_template("verify_failed.html", verify_message=verify_message))
            log = shell.stdout.getvalue().split('\n')
            tree_render = render_node(shell.tree.root, shell.current_node.node_id)
            return render_template('my-form.html', command_history=shell.history, log=log, tree=tree_render, verify_message=verify_render)

        if text == "":
            log = shell.stdout.getvalue().split('\n')
            tree_render = render_node(shell.tree.root, shell.current_node.node_id)
            message = "No Command Entered"
            return render_template('my-form.html', command_history=shell.history, log=log, tree=tree_render, message=message)

        shell.onecmd(text)
        log = shell.stdout.getvalue().split('\n')
        tree_render = render_node(shell.tree.root, shell.current_node.node_id)
        return render_template('my-form.html', command_history=shell.history, log=log, tree=tree_render)

def render_node(node, current_node_id):
    """
    This function compiles the templates and messages with respect to nodes
    """
    children = []
    for child in node.children:
        children.append(render_node(child, current_node_id))
    
    formulas = []
    for formula in node.formulas:
        formula_render = render_formula(formula)
        formulas.append(formula_render)
    
    if node.closed:
        print("closing")
        formulas.append(Markup(closed_string))
    elif node.open:
        print("opening")
        formulas.append(Markup(open_string))
    
    node_html = 'node.html'
    if node.node_id == current_node_id:
        node_html = 'selected_node.html'
        
    node_name = f'Node: {node.node_id}'

    return Markup(render_template(node_html, formulas=formulas, children=children, node=node_name))

def render_formula(formula):
    """
    This function compiles the correct templates and messages with respect to the way formulas are displayed
    """
    formula_html = None

    color_form = "formula_black.html"
    if formula.valid:
        color_form = "formula_blue.html"

    string = f"{formula.formula_id}: {pretty_print(formula.formula)}"

    html_output = render_template(color_form, formula=string)

    if formula.checkmarked:
        html_output += "<span style='color: green'>  &#10003;</span>"

    return Markup(html_output)


@app.route('/test', methods=['GET', 'POST'])
def alpha():
    return "hello"

if __name__=='__main__':
    app.run()