# project_cloud_docker_linux
☁️ Cloud + Docker + Linux + AI: Cloud-Native E-Commerce Platform

Tech Stack
Cloud: Azure (Linux VMs, Load Balancer, DNS, Cloud SQL Database)
Backend: Flask (Python)
Frontend: HTML/CSS/JS generated with Claude.ai
Containerization: Docker (Dockerfile, Docker Hub, Containers)
OS: Linux (Ubuntu-based VMs)
Integration: Gmail API (Email notifications)


📌 Overview
This project is a mini e-commerce platform designed to simulate a real-world workflow using Cloud, Docker, Linux, and AI.
The system allows:

Users to sign up, log in, and place orders.

Orders to be processed and stored in a cloud-hosted SQL database.

Admins to review orders via a console (/admin/all-orders) and either:

Confirm ✅ → customer receives a confirmation email.

Reject ❌ → customer receives a rejection email.

Load Balancer routing tested with two VMs (Server One & Server Two) to ensure scalability.

This project demonstrates the integration of cloud infrastructure, containerization, and AI-generated frontend into one working solution.
