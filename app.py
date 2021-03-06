import peeweedbevolve
from flask import Flask, flash, redirect, render_template, request, url_for
from models import *
import os

app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SECRET_KEY"] = os.getenv('APP_SECRET_KEY')


@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response


@app.cli.command()
def migrate():
    db.evolve(ignore_tables={'base_model'})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stores/new", methods=["GET"])
def show_store_form():
    return render_template("store.html")


@app.route("/stores/new", methods=["POST"])
def create_store():
    # Create a new store using the chosen name
    name = request.form['name']
    s = Store(name=name)

    if s.save():
        flash("Successfully saved")
        return redirect(url_for('show_store_form'))

    return render_template("store.html", name=name, errors=s.errors)


@app.route("/stores")
def show_stores():
    # Selects all the stores in the db
    return render_template("stores.html", stores=Store.select(Store).order_by(Store.id))


@app.route("/stores", methods=["POST"])
def delete_store():
    # Get the id of the store to be deleted
    s = Store.get_by_id(request.form.get('store_id'))
    if s.delete_instance(recursive=True):
        flash("Successfully deleted")
        return redirect(url_for('show_stores'))
    return render_template("store.html", stores=Store.select(Store).order_by(Store.id))


@app.route("/stores/<store_id>")
def show_store(store_id):
    # Selects the store based on the ID provided
    store = Store.get_by_id(store_id)
    return render_template("store_page.html", store=store)


@app.route("/stores/<store_id>", methods=["POST"])
def update_store(store_id):
    u = Store.update(name=request.form.get('new-name')
                     ).where(Store.id == store_id)
    if u.execute():
        flash("Successfully updated")
    return redirect(url_for('show_store', store_id=store_id))


@app.route("/warehouse-management", methods=["GET"])
def show_warehouse_form():
    stores = Store.select()
    return render_template("warehouse.html", stores=stores)


@app.route("/warehouse-management", methods=["POST"])
def create_warehouse():
    # Get the chosen store by the user
    chosen_store = Store.get_by_id(request.form.get('store_id'))

    # Create a new warehouse using the chosen store
    w = Warehouse(location=request.form['location'], store=chosen_store)

    try:
        if w.save():
            flash("Successfully saved")
            return redirect(url_for('show_warehouse_form'))

    except Exception as exc:
        print(exc)
        return render_template("warehouse.html")


if __name__ == 'main':
    app.run()
