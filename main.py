from flask import Flask, request, render_template
import docker


client = docker.from_env()
app = Flask(__name__)


@app.route("/",methods=["GET", "POST"])
def home():
    status = ""

    print(request.get_data())
    if request.method == "POST":
        if request.form.get("create_container") == "Create":
            create_odoo_container()
            ## link doesn't work for some reason right now but otherwise go to localhost:8089 to see odoo dashboard.
            status = "Containers created. Available at <a href=\"localhost:8089\">localhost:8089</a>"

    return render_template("index.html", status=status)


def create_odoo_container():
    ## Cleanup of existing containers to prevent conflicts.
    for container in client.containers.list(all=True):
        print(container.name)
        if container.name in ["db", "odoo"]:
            container.remove(v=True, force=True)

    postgres = client.containers.run(
        "postgres:latest",
        environment={
            "POSTGRES_USER": "odoo",
            "POSTGRES_PASSWORD": "odoo",
            "POSTGRES_DB": "postgres",
        },
        name="db",
        detach=True,
    )

    print("Postgres container created")

    odoo = client.containers.run(
        "odoo:latest",
        ports={"8069/tcp": 8069},
        links={"db": "db"},
        detach=True,
        name="odoo",
    )

    print("Odoo container created")


if __name__ == "__main__":    
    app.run(
        debug=True,
        use_debugger = False
    )
