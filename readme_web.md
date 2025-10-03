# **Deployment Guide for Render**

This guide will walk you through deploying your Flask application to Render using the provided configuration files. The setup includes a web service for the application, a persistent disk for the SQLite database, and an automated daily cron job to update the data.

## **Step 1: Finalize Your Project Files**

Ensure your project directory has the following structure and files. This is crucial for the deployment to work correctly.  
/  
|-- data/  
|   |-- arxiv.db         \<-- Your initial SQLite database file  
|-- templates/  
|   |-- index.html       \<-- Your HTML template  
|-- app.py               \<-- Your main Flask application  
|-- update\_database.py   \<-- Your daily database update script  
|-- render.yaml          \<-- The deployment blueprint  
|-- requirements.txt     \<-- Python dependencies

## **Step 2: Push to GitHub**

Commit all of these files to your GitHub repository. It is important to **include the initial data/arxiv.db database file**. This file will be copied to Render's persistent disk on the first deploy, populating your application with its starting data.  
Run these commands in your terminal:  
\# Add all the necessary files to git  
git add app.py update\_database.py render.yaml requirements.txt templates/ data/

\# Commit the changes  
git commit \-m "feat: Prepare application for Render deployment"

\# Push to your main branch  
git push

## **Step 3: Deploy on Render**

1. Log in to your [Render Dashboard](https://dashboard.render.com/).  
2. Click the **New \+** button and select **Blueprint**.  
3. Connect the GitHub repository containing your project.  
4. Render will automatically detect and begin configuring your project based on the render.yaml file.  
5. On the configuration screen, you will be prompted to provide values for the secret environment variables (GITHUB\_API\_KEY, GEMINI\_API\_KEY, etc.). **Securely paste your keys and other required values into these fields.**  
6. Click **Apply** to start the deployment.

Render will now build your application, install the dependencies from requirements.txt, set up the persistent disk, and start your web service. This first deployment may take a few minutes.

## **Step 4: Verify Your Deployment**

Once the deployment is complete, Render will provide a public URL for your live web service (e.g., https://arxiv-star-viewer.onrender.com). Visit this URL to ensure your application is running correctly and displaying data from the database.  
Your cron job is scheduled to run daily at 8:00 AM UTC. You can monitor its status and view logs in the **Cron** section of your service on the Render dashboard to confirm that your update\_database.py script is executing successfully.