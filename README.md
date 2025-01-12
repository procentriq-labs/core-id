# ProcentrIQ CoreID
CoreID: A simple identity provider / authorization server handling authentication and user account management for ProcentrIQ projects

[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

## Features

- [ ] **Authorization Code Flow** for login of human users from trusted clients
- [ ] **Client Credentials Flow** for authorization of machine2machine apps
- [ ] **Refresh Token Flow** to limit validity of access token
- [ ] **Scopes** on a per-resource level
- [ ] **Dynamic Client Registration** for creating new API credentials dynamically
- [ ] Expose **OpenID configuration**
- [ ] Expose **JSON Web Key Sets** for easy verification of issued JWTs

## Setup Instructions

Follow these steps to set up the application, generate necessary keys, and configure the environment.

### Prerequisites
- Python 3.8 or later
- Docker and Docker Compose (if using the containerized setup)
- OpenSSL or `ssh-keygen` for generating RSA keys

---

### 1. Clone the Repository
```bash
git clone git@github.com:procentriq-labs/core-id.git
cd core-id
```

---

### 2. Install the Tailwind CLI

See [Install the TailwindCSS CLI](https://tailwindcss.com/blog/standalone-cli).

---

### 3. Create RSA Keys for JWT signing
The application requires RSA keys to sign and verify JSON Web Tokens (JWTs). You can generate them using `ssh-keygen`:

#### **Generate a Private Key**
Run the following command to generate a 2048-bit RSA private key:
```bash
ssh-keygen -t rsa -b 2048 -m PEM -f config/jwt.pem
```

#### **Verify the Keys**
To ensure the key is correctly generated:
```bash
cat config/jwt.pem
```

> ⚠️ **Important**: Keep the private key (`jwt.pem`) secure and do not commit it to version control. It is included in the `.gitignore`

---

### 4. Configure the application

1. The application uses environment variables for sensitive settings. A `.env.example` file is provided as a template.
1. Configure the application by adjusting the `coreid.yaml` file in the `config` folder.

---

### 5. Set Up Python Environment
#### **Create and Activate a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```

#### **Install Dependencies**
```bash
pip install -r requirements.txt
```

---

### 6. Database Setup
#### **Run Migrations**
The application uses Alembic for database migrations. Run the following command to initialize the database:
```bash
just db-upgrade
```

---

### 7. Start the Application
#### **Local Development**
Start the application with the following command:
```bash
python src/app/main.py
```

#### **Docker (Optional)**
To run the application using Docker Compose:
```bash
just build && just up
```

---

### 8. Access the Application

Info available at `/.well-known/openid-configuration`.

---

### Notes
- **Environment-Specific Configurations**: Use `.env` and `coreid.yaml` to customize the application for different environments.
- **Key Rotation**: Periodically rotate your RSA keys to enhance security.
- **Secure the Private Key**: Ensure the private key is accessible only to authorized users or processes.


## Acknowledgements

This project wouldn't have been possible without the amazing work of:

- [JinjaX](https://github.com/jpsca/jinjax) - A server-side component engine for Jinja
- [BasicComponents](https://github.com/basicmachines-co/basic-components) - shadcn/ui components ported to JinjaX

## License

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg