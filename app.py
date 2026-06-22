from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for
)

from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import os

load_dotenv()

app = Flask(__name__)
app.secret_key = "internship_tracker_secret_key"

# MongoDB

client = MongoClient(os.getenv("MONGO_URI"))

db = client["internship_tracker"]

applications = db["applications"]
users = db["users"]


# --------------------------
# LOGIN CHECK HELPER
# --------------------------

def is_logged_in():
    return "user_id" in session


# --------------------------
# HOME
# --------------------------

@app.route("/")
def home():

    if not is_logged_in():
        return redirect("/login")

    user_id = session["user_id"]

    search = request.args.get("search", "")
    status_filter = request.args.get("status", "")

    query = {
        "user_id": user_id
    }

    if search:
        query["company"] = {
            "$regex": search,
            "$options": "i"
        }

    if status_filter:
        query["status"] = status_filter

    apps = list(
        applications.find(query)
    )

    total = applications.count_documents({
        "user_id": user_id
    })

    applied = applications.count_documents({
        "user_id": user_id,
        "status": "Applied"
    })

    interviews = applications.count_documents({
        "user_id": user_id,
        "status": "Interview"
    })

    offers = applications.count_documents({
        "user_id": user_id,
        "status": "Offer"
    })

    rejected = applications.count_documents({
        "user_id": user_id,
        "status": "Rejected"
    })

    return render_template(
        "index.html",
        apps=apps,
        total=total,
        applied=applied,
        interviews=interviews,
        offers=offers,
        rejected=rejected,
        search=search,
        status_filter=status_filter,
        username=session["username"]
    )


# --------------------------
# REGISTER
# --------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = users.find_one({
            "email": email
        })

        if existing_user:
            return "Email already registered"

        hashed_password = generate_password_hash(
            password
        )

        users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password
        })

        return redirect("/login")

    return render_template(
        "register.html"
    )


# --------------------------
# LOGIN
# --------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = users.find_one({
            "email": email
        })

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = str(
                user["_id"]
            )

            session["username"] = user[
                "username"
            ]

            return redirect("/")

        return "Invalid Credentials"

    return render_template(
        "login.html"
    )


# --------------------------
# LOGOUT
# --------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# --------------------------
# ADD APPLICATION
# --------------------------

@app.route("/add", methods=["POST"])
def add_application():

    if not is_logged_in():
        return redirect("/login")

    applications.insert_one({

        "user_id": session["user_id"],

        "company":
        request.form.get("company"),

        "role":
        request.form.get("role"),

        "status":
        request.form.get("status"),

        "notes":
        request.form.get("notes")

    })

    return redirect("/")


# --------------------------
# DELETE APPLICATION
# --------------------------

@app.route("/delete/<id>")
def delete(id):

    if not is_logged_in():
        return redirect("/login")

    applications.delete_one({
        "_id": ObjectId(id),
        "user_id": session["user_id"]
    })

    return redirect("/")


# --------------------------
# EDIT APPLICATION
# --------------------------

@app.route(
    "/edit/<id>",
    methods=["GET", "POST"]
)
def edit(id):

    if not is_logged_in():
        return redirect("/login")

    app_data = applications.find_one({

        "_id": ObjectId(id),

        "user_id":
        session["user_id"]

    })

    if not app_data:
        return redirect("/")

    if request.method == "POST":

        applications.update_one(

            {
                "_id": ObjectId(id)
            },

            {
                "$set": {

                    "company":
                    request.form.get(
                        "company"
                    ),

                    "role":
                    request.form.get(
                        "role"
                    ),

                    "status":
                    request.form.get(
                        "status"
                    ),

                    "notes":
                    request.form.get(
                        "notes"
                    )

                }
            }

        )

        return redirect("/")

    return render_template(
        "edit.html",
        app=app_data
    )


if __name__ == "__main__":
    app.run(debug=True)