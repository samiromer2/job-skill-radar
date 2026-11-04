# Plan: close the CI/CD, Docker and AWS gaps (plus AWS Cloud Practitioner)

_Written 2026-10-12 for Samir, updated 2026-10-13 for the larger dataset. Based on [skill-gap-report.md](/mnt/project-files/market/skill-gap-report.md) and [resume-vs-applications.md](/mnt/project-files/market/resume-vs-applications.md). Across the 262 jobs you applied to or packaged, the skills your CV doesn't show are led by CI/CD (84 postings), security (76), AWS (71) and Docker (57). Kubernetes (36) is new on the list, and 79 of the roles are senior, staff or lead._

## 1. Is your approach right?

Yes, mostly. One project that covers Docker, GitHub Actions and AWS is the right move. It answers your top four gaps with one link you can put on your CV, since those four now make up the top of the list. I'd change five things:

1. **Fold security into the same project.** Security is your second-biggest gap (76 postings), close behind CI/CD (84). A modern pipeline already gives you most of it for free: dependency scanning, container image scanning, code scanning, and deploying with short-lived credentials instead of stored AWS keys. Add login (JWT) if the app doesn't have it yet. Then the project answers four gaps, not three.
2. **Your CV says Azure AI-900, not AZ-900.** AI-900 is the AI fundamentals exam. AZ-900 is the general Azure fundamentals exam, and it overlaps more with Cloud Practitioner. You still know the Azure side from App Service and Functions work, so the cert is very doable. Just don't write "AZ-900" anywhere unless you hold it.
3. **List what you already have under CI/CD.** Auto-deploys from GitHub to Vercel, Azure App Service or Static Web Apps count as continuous deployment. Put those on the CV now, honestly worded, before the new project is done.
4. **Use Lambda, not EC2 or ECS, on AWS.** A Docker image on AWS Lambda costs almost nothing and scales to zero. ECS Fargate needs a load balancer (about US$16/month on its own), and EC2 runs all day. You still use Docker, ECR and IAM, which are the words postings ask for.
5. **Give it 3 weeks for the project and 4 for the cert, side by side.** At about 1 to 1.5 hours on weekdays and a few hours on weekends, this is realistic. Two weeks is tight if you also want tests, security and a good README.

## 2. Which project to use

Use **your strongest Python/FastAPI project**, ideally one that has a database and a handful of endpoints you'd be happy to demo in an interview. I didn't open your GitHub repos, so pick the one that fits this best.

Why FastAPI and not Laravel or the Rails consent portal:
- Python is your strongest match (153 of your 262 postings) and FastAPI is already on your CV.
- FastAPI has built-in test tooling and OpenAPI docs, so CI and a live demo come easily.
- Python on Lambda is very well documented, so you'll spend your time on the pipeline and not on fighting the platform.
- The Rails portal was interview prep and doesn't match your stack.

If your best project is Laravel, the same plan works. Swap the Dockerfile base image for `php:8.3-fpm` (with nginx or FrankenPHP) and the test step for `php artisan test`. Lambda is harder with PHP, so you'd deploy to a single EC2 instance or App Runner instead.

## 3. What you'll end up with

```
 push / PR                     merge to main
     │                              │
     ▼                              ▼
┌────────────── GitHub Actions ───────────────────────────────┐
│ lint (ruff) → tests (pytest + Postgres) → docker build      │
│ → image scan (Trivy) → smoke test                           │
│                         └─ main only → OIDC login to AWS    │
│                            → push image to ECR              │
│                            → update Lambda → live smoke test│
└─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
            AWS: Lambda (your container) ──► RDS PostgreSQL (free tier)
                 public Function URL
```

Done looks like this:
- [ ] `docker compose up` runs the app and Postgres locally with one command.
- [ ] Every pull request runs lint, tests, a Docker build and a security scan, and can't merge if they fail.
- [ ] Every merge to `main` deploys to AWS without anyone touching the console.
- [ ] No AWS keys are stored in GitHub.
- [ ] A live URL, a README with a diagram and status badges, and a budget alert that has never fired.

## 4. Week by week

### Week 1: Docker and CI

| Day | Do |
|---|---|
| 1 | Pick the repo. Create a `ci-cd` branch. Add a `GET /health` endpoint that returns `{"status": "ok"}` and doesn't touch the database. Make sure the app reads its database URL from a `DATABASE_URL` environment variable. |
| 2 | Write or tidy 10 to 15 real tests with `pytest` and FastAPI's `TestClient`. Cover the main endpoints, one failure case each, and `/health`. Add `requirements-dev.txt` (pytest, pytest-cov, ruff, httpx). |
| 3 | Add the `Dockerfile`, `.dockerignore` and `docker-compose.yml` from section 5. Run `docker compose up --build` and check `http://localhost:8000/docs`. |
| 4 | Add `.github/workflows/pipeline.yml` from section 6, but only the `test` and `build` jobs for now. Open a pull request and watch it run. Fix it until it's green. |
| 5 | In GitHub, go to Settings → Branches → add a rule for `main`: require a pull request and require the `test` and `build` checks to pass. Add `.github/dependabot.yml` (section 6). Merge. |
| Weekend | Break a test on purpose and open a PR to see it blocked. This gives you a real story for interviews ("the pipeline caught..."). |

### Week 2: AWS deploy

| Day | Do |
|---|---|
| 1 | Set up the AWS account safely (section 7, step 1) and the budgets (section 8). Do this before creating anything else. |
| 2 | Create the ECR repository and the RDS database (section 7, steps 2 and 3). RDS takes about 10 minutes to start. |
| 3 | Push the first image by hand from your laptop and create the Lambda function from it (section 7, steps 4 and 5). Open the Function URL and hit `/health` and `/docs`. |
| 4 | Set up GitHub OIDC and the deploy role (section 7, step 6). Add the repo variables (step 7). |
| 5 | Add the `deploy` job to the workflow. Merge a small change and watch it go live by itself. |
| Weekend | Run your database migrations against RDS (for example `alembic upgrade head` from a short one-off task, or at app startup for a demo), and try the whole flow end to end. |

### Week 3: security and polish

| Day | Do |
|---|---|
| 1 | If the app has no login, add OAuth2 password flow with JWT (FastAPI's security tutorial covers it) and protect the write endpoints. Hash passwords with `bcrypt` or `argon2`. |
| 2 | Turn on CodeQL (Settings → Code security → Code scanning → Default setup) and secret scanning. Pin third-party actions to a full commit SHA (Dependabot will keep them updated). |
| 3 | Write the README: what the app does, the diagram above, how to run it locally, how the pipeline works, what it costs, and CI status badges. |
| 4 | Update your CV and LinkedIn (section 10). |
| 5 | Do a teardown drill: write down what you'd delete to bring the bill to $0 (section 8) so you're never worried about leaving it running. |

### Cert, alongside weeks 1 to 4

See section 9. About 30 to 45 minutes a day, practice exams in weeks 3 and 4, and the exam at the end of week 4.

## 5. Docker files

These assume your code lives in `app/` with the FastAPI object at `app/main.py` as `app`. Adjust the paths to your repo.

**`Dockerfile`**. One image runs on your laptop, in CI and on Lambda. The AWS Lambda Web Adapter is a small add-on that sits idle anywhere except Lambda, so you don't need a second handler or library like Mangum.

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    AWS_LWA_READINESS_CHECK_PATH=/health

WORKDIR /srv

# Install dependencies first so this layer is cached between code changes
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

# Lets the same image run on AWS Lambda; does nothing anywhere else.
# Check https://github.com/awslabs/aws-lambda-web-adapter for the latest version.
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1 /lambda-adapter /opt/extensions/lambda-adapter

# Don't run as root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
```

**`.dockerignore`**

```
.git
.github
.venv
__pycache__/
*.pyc
.pytest_cache
.env
tests/
docker-compose.yml
```

**`docker-compose.yml`** (local development only)

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      retries: 10

  api:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://app:app@db:5432/app
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
```

Commands you'll use:

```bash
docker compose up --build        # run everything
docker compose down              # stop
docker compose down -v           # stop and wipe the local database
docker build -t myapp . && docker run -p 8000:8000 -e DATABASE_URL=... myapp
```

## 6. The GitHub Actions pipeline

Create `.github/workflows/pipeline.yml`. It has three jobs. `test` and `build` run on every pull request and push. `deploy` runs only on pushes to `main`, after both pass.

```yaml
name: Pipeline

on:
  pull_request:
  push:
    branches: [main]

# Least privilege by default; the deploy job asks for more
permissions:
  contents: read

concurrency:
  group: pipeline-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: app
          POSTGRES_PASSWORD: app
          POSTGRES_DB: app_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U app"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
    env:
      DATABASE_URL: postgresql://app:app@localhost:5432/app_test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - name: Lint
        run: |
          ruff check .
          ruff format --check .
      - name: Test
        run: pytest --cov=app --cov-report=term-missing

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Build image
        uses: docker/build-push-action@v6
        with:
          context: .
          load: true
          tags: app:ci
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - name: Scan image for vulnerabilities
        uses: aquasecurity/trivy-action@0.28.0   # pin to a commit SHA in week 3
        with:
          image-ref: app:ci
          severity: CRITICAL,HIGH
          ignore-unfixed: true
          exit-code: "1"
      - name: Smoke test the container
        run: |
          docker run -d --name app -p 8000:8000 \
            -e DATABASE_URL=postgresql://unused:unused@localhost:5432/unused app:ci
          for i in $(seq 1 20); do
            curl -fsS http://localhost:8000/health && exit 0
            sleep 1
          done
          docker logs app
          exit 1

  deploy:
    needs: [test, build]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    permissions:
      contents: read
      id-token: write   # lets GitHub hand AWS a short-lived identity token
    steps:
      - uses: actions/checkout@v4

      - name: Log in to AWS (no stored keys)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}

      - id: ecr
        uses: aws-actions/amazon-ecr-login@v2

      - uses: docker/setup-buildx-action@v3

      - name: Build and push image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          platforms: linux/amd64
          provenance: false   # Lambda can't read multi-manifest images
          tags: ${{ steps.ecr.outputs.registry }}/${{ vars.ECR_REPOSITORY }}:${{ github.sha }}
          cache-from: type=gha

      - name: Update Lambda
        env:
          IMAGE: ${{ steps.ecr.outputs.registry }}/${{ vars.ECR_REPOSITORY }}:${{ github.sha }}
        run: |
          aws lambda update-function-code \
            --function-name "${{ vars.LAMBDA_FUNCTION }}" \
            --image-uri "$IMAGE"
          aws lambda wait function-updated --function-name "${{ vars.LAMBDA_FUNCTION }}"

      - name: Smoke test production
        run: curl -fsS "${{ vars.FUNCTION_URL }}health"
```

What each part buys you, in interview terms:
- **`services: postgres`** runs your tests against a real database, not mocks.
- **`needs:`** makes it a pipeline: no deploy unless lint, tests, build and scan all pass.
- **Trivy** fails the build on known critical or high vulnerabilities in the image.
- **OIDC (`id-token: write`)** means GitHub gets a temporary AWS login per run, scoped to this repo and the `production` environment. There's no access key to leak.
- **`environment: production`** lets you add a manual approval later (Settings → Environments → Required reviewers).
- **Tagging images with the commit SHA** means you can roll back by pointing Lambda at an older tag.

**`.github/dependabot.yml`**

```yaml
version: 2
updates:
  - package-ecosystem: pip
    directory: "/"
    schedule: { interval: weekly }
  - package-ecosystem: github-actions
    directory: "/"
    schedule: { interval: weekly }
  - package-ecosystem: docker
    directory: "/"
    schedule: { interval: weekly }
```

## 7. AWS setup, one time

Use region **ca-central-1 (Canada Central)** for everything.

**Step 1: Lock down the account.**
1. Sign up, then turn on MFA for the root user. Don't create access keys for root, ever.
2. Create an everyday admin login through IAM Identity Center (or an IAM user with MFA) and use that from now on.
3. On your laptop, install the AWS CLI and run `aws configure sso` (or `aws configure`) with that login.

**Step 2: ECR (where your images live).**
```bash
aws ecr create-repository --repository-name myapp \
  --image-scanning-configuration scanOnPush=true
```
Then add a lifecycle rule in the console (ECR → myapp → Lifecycle policy) to keep only the last 5 images. This keeps you under the free 500 MB.

**Step 3: RDS PostgreSQL (skip if your app has no database).**
Console → RDS → Create database → PostgreSQL → **Free tier** template. Use `db.t4g.micro`, 20 GB storage, storage autoscaling **off**, public access **No**, default VPC, a new security group named `rds-sg`. Turn off Performance Insights extras and set backup retention to 1 day. Note the endpoint and password.

**Step 4: First image, pushed by hand.**
```bash
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REGION=ca-central-1
REG=$ACCOUNT.dkr.ecr.$REGION.amazonaws.com
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REG
docker buildx build --platform linux/amd64 --provenance=false -t $REG/myapp:first --push .
```

**Step 5: Lambda function.**
Console → Lambda → Create function → **Container image** → pick `myapp:first`. Architecture x86_64. Then:
- Configuration → General: memory 512 MB, timeout 15 s.
- Configuration → Environment variables: `DATABASE_URL=postgresql://USER:PASS@RDS-ENDPOINT:5432/DBNAME`. Lambda encrypts these at rest. Fine for a portfolio app.
- Configuration → VPC (only with RDS): attach the default VPC, two subnets, and a new security group `lambda-sg`. Then edit `rds-sg` to allow port 5432 **from `lambda-sg` only**. The function's role needs the `AWSLambdaVPCAccessExecutionRole` policy (the console offers to add it). Note: a Lambda inside the VPC can't reach the internet. That's fine unless your app calls an outside API (an LLM, for example). If it does, keep Lambda out of the VPC and tell me, because the database setup changes.
- Configuration → Function URL → Create → Auth type **NONE**. This is your public URL.
- Configuration → Concurrency: set reserved concurrency to 5 if the console lets you. New accounts are often capped at 10 in total anyway, which also limits runaway cost.
- CloudWatch → Log groups → `/aws/lambda/<function>` → set retention to 1 week.

**Step 6: Let GitHub deploy without keys (OIDC).**
1. IAM → Identity providers → Add provider → OpenID Connect. Provider URL `https://token.actions.githubusercontent.com`, audience `sts.amazonaws.com`.
2. IAM → Roles → Create role → Web identity → that provider. Then replace its trust policy with this one, which only lets the `production` environment of your one repo use it:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
        "token.actions.githubusercontent.com:sub": "repo:samiromer2/REPO_NAME:environment:production"
      }
    }
  }]
}
```

3. Attach an inline permissions policy that can only push to your one ECR repo and update your one function:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": "ecr:GetAuthorizationToken", "Resource": "*" },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability", "ecr:BatchGetImage",
        "ecr:InitiateLayerUpload", "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload", "ecr:PutImage"
      ],
      "Resource": "arn:aws:ecr:ca-central-1:ACCOUNT_ID:repository/myapp"
    },
    {
      "Effect": "Allow",
      "Action": ["lambda:UpdateFunctionCode", "lambda:GetFunction", "lambda:GetFunctionConfiguration"],
      "Resource": "arn:aws:lambda:ca-central-1:ACCOUNT_ID:function:FUNCTION_NAME"
    }
  ]
}
```

Name the role `github-deploy-myapp`.

**Step 7: GitHub settings.**
- Settings → Environments → New environment → `production`.
- Settings → Secrets and variables → Actions → **Variables** (not secrets, since none of these are secret):
  - `AWS_DEPLOY_ROLE_ARN` = the role's ARN
  - `AWS_REGION` = `ca-central-1`
  - `ECR_REPOSITORY` = `myapp`
  - `LAMBDA_FUNCTION` = your function name
  - `FUNCTION_URL` = the Function URL, ending in `/`

## 8. Cost guardrails

**What it should cost:** $0 while you're on the free tier or free credits. Lambda's 1 million requests a month and DynamoDB are always free. ECR's 500 MB and RDS's 750 hours of `db.t4g.micro` are free for the first 12 months on older accounts. New accounts opened since July 2025 get a credit-based Free plan instead (US$100 at sign-up plus up to US$100 more for completing setup tasks, for 6 months), which covers this easily. Check the Billing console after sign-up to see which one you have. Once free usage ends, RDS is the only real cost, roughly US$13 to $15 a month (my estimate from on-demand pricing; check the AWS pricing calculator).

**Do these on day 1 of week 2:**
1. Billing → Budgets → Create budget → **Zero spend budget** template. It emails you the moment anything costs a cent.
2. A second budget: monthly cost, US$5, alerts at 50% and 100%.
3. Billing preferences → turn on **Free Tier usage alerts**.

**Never create these for this project.** They're the usual surprise bills:
- **NAT Gateway** (about US$32/month plus data). You don't need one with this setup.
- **Application Load Balancer** (about US$16/month idle).
- **EKS** (about US$73/month for the control plane alone).
- **VPC interface endpoints** (about US$7/month each).
- An **Elastic IP** that isn't attached to a running instance.
- Anything Multi-AZ, or RDS bigger than `micro`.

**Habits:**
- Stopping RDS saves money, but AWS restarts it after 7 days. If you won't use it for a while, take a snapshot and delete it.
- Keep the ECR lifecycle rule (5 images) and 1-week log retention.
- Check Billing → Bills once a week for the first month.

**Teardown, in order, if you ever want $0:** delete the Lambda function, the RDS instance (and its snapshots), the ECR repository, the CloudWatch log group, then the IAM role and OIDC provider. Leave the budgets in place.

## 9. AWS Certified Cloud Practitioner study plan

**The exam** (CLF-C02 at the time of writing; check the current exam guide on the AWS site before booking): 65 questions, 90 minutes, pass mark 700/1000, US$100, online or at a test centre. The domains are Cloud Concepts (24%), Security and Compliance (30%), Cloud Technology and Services (34%), and Billing, Pricing and Support (12%).

**Your head start:** you already know the Azure versions of most services. Make a one-page map as you go:

| Azure | AWS |
|---|---|
| App Service | Elastic Beanstalk / App Runner |
| Functions | Lambda |
| Blob Storage | S3 |
| Azure SQL / PostgreSQL | RDS / Aurora |
| Cosmos DB | DynamoDB |
| Entra ID | IAM / IAM Identity Center |
| Azure Monitor | CloudWatch |
| VNet / NSG | VPC / Security Group |
| Azure Container Registry | ECR |
| Cost Management | Cost Explorer / Budgets |
| Azure Advisor | Trusted Advisor |

**Resources:**
- Free: AWS Skill Builder, "AWS Cloud Practitioner Essentials" course, and the official practice question set.
- Paid and widely used: Stephane Maarek's Udemy course (watch at 1.5x and skip what you know from Azure), and Tutorials Dojo practice exams (Jon Bonso).

**Schedule (30 to 45 minutes a day):**

| Week | Focus |
|---|---|
| 1 | Cloud concepts, global infrastructure, IAM and the shared responsibility model. Book the exam for the end of week 4 so there's a date. |
| 2 | Compute, storage, databases and networking. The project is in AWS this week, so the services will feel familiar. |
| 3 | Security services (GuardDuty, Inspector, Shield, WAF, KMS, Config, CloudTrail), billing, pricing models, support plans and the Well-Architected Framework. First full practice exam. |
| 4 | Two or three more practice exams. Review every wrong answer. Take the real exam once you score 80%+ on practice tests. |

## Stretch for senior roles (week 4 or later)

79 of your roles are senior, staff or lead, and 36 postings ask for Kubernetes. Senior interviewers expect you to own the pipeline and the infrastructure, not only the app. Do these after the core project works, never instead of it:

1. **Terraform for the AWS pieces.** Describe the ECR repository, Lambda function, IAM role and budgets in Terraform, and add a `terraform plan` step to pull requests. Then you can say the infrastructure is code-reviewed like the app. Terraform isn't in the posting counts, so this one is my judgement of what senior DevOps questions cover.
2. **Kubernetes without paying for it.** Don't use EKS (about US$73/month). Add a CI job that starts a throwaway cluster with `kind` (helm/kind-action), deploys your image with a small Deployment and Service manifest, and curls `/health`. It's free, it proves the image runs on Kubernetes, and "Kubernetes (manifests, kind)" can then go on the CV honestly.

Node.js (41 postings) and Rails (33) are real gaps too, but they're separate projects and don't belong in this one.

## 10. How to put it on your CV and LinkedIn

**The rule:** only list what's real on the day you send the CV. You can say "in progress" with a date for the cert, but not for the pipeline.

**Right now, before the project:** under Skills, add a CI/CD line with the deploy pipelines you've genuinely set up, for example `CI/CD: automated deploys to Vercel and Azure App Service from GitHub`. Fix any "AZ-900" wording to "AI-900".

**Skills section, once the project is live.** Use the exact words applicant tracking systems scan for:

> **DevOps & Cloud:** CI/CD (GitHub Actions), Docker, Docker Compose, AWS (Lambda, ECR, RDS, IAM, OIDC, CloudWatch), Azure (App Service, Functions, Static Web Apps), Trivy, CodeQL, Dependabot

**Projects section, one entry with a link:**

> **[Project name]**, Python, FastAPI, PostgreSQL, Docker, GitHub Actions, AWS · [github link] · [live link]
> - Containerized a FastAPI and PostgreSQL service with Docker and Docker Compose; one image runs locally, in CI and on AWS Lambda.
> - Built a GitHub Actions pipeline that lints, runs tests against a real Postgres database, scans the image with Trivy and blocks merges on failure.
> - Automated deployment to AWS (ECR and Lambda) on every merge using OIDC short-lived credentials, with no stored cloud keys and least-privilege IAM.
> - Added JWT authentication, CodeQL scanning and Dependabot; runs at $0/month within the AWS free tier with budget alerts.

**Certifications:** `AWS Certified Cloud Practitioner (in progress, exam booked for [month] 2026)` until you pass, then `AWS Certified Cloud Practitioner, [month] 2026` with the Credly badge link.

**Elsewhere:**
- Put the live link and the repo in LinkedIn's Featured section. Add the cert under Licenses and Certifications.
- If you also have pipelines at Bitcoin Innovation Hub or Carlington CHC, add one bullet to that job, because work experience counts more than a side project. Only if it's true.
- In the developer version of your CV, mention this project in your summary line too ("...with CI/CD and AWS deployment experience").

## 11. Interview talking points you'll have afterwards

- Why Lambda over ECS for this app (cost, scale to zero, traffic pattern), and when you'd pick ECS instead (long-running work, steady traffic, WebSockets).
- Why OIDC instead of access keys, and how the trust policy limits it to one repo and environment.
- How you'd roll back (point Lambda at the previous image tag).
- What the pipeline caught (the broken test you merged on purpose in week 1, or a real Trivy finding).
- How you kept the bill at zero.
