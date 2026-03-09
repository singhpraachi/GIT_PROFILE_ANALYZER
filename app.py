from flask import Flask, render_template, request
import requests
import matplotlib.pyplot as plt
import csv

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():

    user_data = None
    repos = []
    languages = {}
    top_repos = []
    score = None
    error = None

    if request.method == "POST":

        username = request.form["username"]

        profile_url = f"https://api.github.com/users/{username}"
        repos_url = f"https://api.github.com/users/{username}/repos"

        profile_response = requests.get(profile_url)

        if profile_response.status_code == 404:

            error = "GitHub user not found. Please check the username."

        elif profile_response.status_code == 200:

            user_data = profile_response.json()

            repo_response = requests.get(repos_url)
            repos = repo_response.json()

            # Language usage
            for repo in repos:
                lang = repo["language"]
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1

            # Top 5 repos
            repos_sorted = sorted(
                repos,
                key=lambda x: x["stargazers_count"],
                reverse=True
            )

            top_repos = repos_sorted[:5]

            # Total stars
            total_stars = sum(repo["stargazers_count"] for repo in repos)

            # Profile score
            score = (
                user_data["followers"] * 2
                + total_stars * 3
                + user_data["public_repos"]
            )

            # Language chart
            if languages:

                names = list(languages.keys())
                values = list(languages.values())

                plt.figure()

                plt.bar(names, values)

                plt.title("Language Usage")

                plt.xlabel("Language")
                plt.ylabel("Repositories")

                plt.savefig("static/language_chart.png")

                plt.close()

            # CSV export
            with open("static/report.csv", "w", newline="") as file:

                writer = csv.writer(file)

                writer.writerow(["GitHub Profile Report"])
                writer.writerow([])

                writer.writerow(["Name", user_data["name"]])
                writer.writerow(["Username", user_data["login"]])
                writer.writerow(["Followers", user_data["followers"]])
                writer.writerow(["Following", user_data["following"]])
                writer.writerow(["Public Repositories", user_data["public_repos"]])
                writer.writerow(["GitHub Score", score])

                writer.writerow([])
                writer.writerow(["Languages Used"])

                for lang, count in languages.items():
                    writer.writerow([lang, count])

                writer.writerow([])
                writer.writerow(["Top Repositories"])
                writer.writerow(["Repository", "Stars"])

                for repo in top_repos:
                    writer.writerow([repo["name"], repo["stargazers_count"]])

    return render_template(
        "index.html",
        user=user_data,
        repos=repos,
        languages=languages,
        top_repos=top_repos,
        score=score,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)