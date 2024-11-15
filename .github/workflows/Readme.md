# Table of Contents

1. [Build Workflow](#build-workflow)  
2. [Deploy Workflow](#deploy-workflow)  
3. [Run Tests on Code](#test-code-workflow)  
4. [Run Tests on Container](#test-container-workflow)  
5. [Tag Release](#tag-release)  
6. [Continuous Integration & Continuous Deployment Workflow](#cicd-pipeline-workflow)  

# Build Workflow

The workflow builds a Docker image from the repository. It allows the user to specify various build parameters, including the Docker image tag, the source revision or branch, and the platforms to build for. Additionally, the workflow can optionally rebuild the image or push the latest tag.

---

## Workflow Inputs

| Input Name   | Description                                              | Type      | Default Value                 | Required | Options                           |
|--------------|----------------------------------------------------------|-----------|-------------------------------|----------|-----------------------------------|
| `img_tag`    | Docker image tag.                                         | `string`  | None                          | Yes      | N/A                               |
| `ref`        | Revision or branch to build.                             | `string`  | `main`                        | No       | N/A                               |
| `push_latest`| Set to `true` to push the image as the latest version.    | `boolean` | `false`                       | No       | N/A                               |
| `platforms`  | Platforms to build for.                                  | `choice`  | `linux/amd64,linux/arm64`     | No       | `linux/amd64`, `linux/arm64`, `linux/amd64,linux/arm64` |
| `rebuild`    | Set to `true` to forcefully rebuild the image.            | `boolean` | `false`                       | No       | N/A                               |

---

## Triggers

This workflow is triggered manually via the **`workflow_dispatch`** event in GitHub Actions. Users can specify input parameters when initiating the workflow.

---

## Job Details

### Job: `build-image`

- **Runs on:** `ubuntu-latest`
- **Permissions:**
  - `contents: read`: To fetch repository contents.
  - `packages: write`: To publish Docker images to GitHub Container Registry (GHCR).

#### Steps

1. **Build Image**
   - **Action Used:** `hathitrust/github_actions/build@v1.4.0`
   - **Inputs Passed to Action:**
     - `image`: Name of the image to build (`ghcr.io/${{ github.repository }}`).
     - `dockerfile`: Dockerfile to use (`Dockerfile`).
     - `img_tag`: Image tag specified by the user (`${{ inputs.img_tag }}`).
     - `tag`: Revision or branch to build (`${{ inputs.ref }}`).
     - `push_latest`: Whether to push the image as `latest` (`${{ inputs.push_latest }}`).
     - `registry_token`: Authentication token (`${{ github.token }}`).
     - `rebuild`: Whether to rebuild the image (`${{ inputs.rebuild }}`).

---

## Notes

- **Docker Platforms Support:** This workflow allows building for multiple architectures (`linux/amd64` and/or `linux/arm64`), making it suitable for cross-platform deployments.
- **GHCR Integration:** Built images are pushed to GitHub Container Registry (`ghcr.io`), ensuring seamless integration with GitHub-hosted projects.
- **Manual Execution:** As this workflow is manually triggered, it is ideal for controlled builds or testing scenarios.

---

## How to Use

1. Navigate to the **Actions** tab in your GitHub repository.
2. Select the **Build** workflow from the list.
3. Click **Run Workflow**.
4. Fill out the input fields as needed:
   - Provide a custom `img_tag` (e.g., `v1.0.0`).
   - Specify a branch or revision in `ref` (default is `main`).
   - Enable or disable optional fields like `push_latest` or `rebuild`.
5. Click **Run Workflow** to start the build process.

---

## Example

### Triggering the Workflow with Inputs

Run the workflow with the following inputs:

- **img_tag:** `v1.0.0`
- **ref:** `main`
- **platforms:** `linux/amd64`
- **push_latest:** `true`
- **rebuild:** `false`

This will:
- Build a Docker image tagged as `v1.0.0`.
- Use the `main` branch for the build.
- Build for `linux/amd64`.
- Push the image as `latest`.

--- 

# Deploy Workflow

---

## Purpose

The workflow enables controlled deployment of Docker images to specific nvironments: **testing**, **staging**, or **production**, by updating the configuration in the ArgoCD control repository. This ensures the deployed application points to the correct image version.

---

## Workflow Inputs

| Input Name     | Description                           | Type      | Default Value | Required | Options                |
|----------------|---------------------------------------|-----------|---------------|----------|------------------------|
| `branch_hash`  | Branch hash or revision to deploy.    | `string`  | `main`        | No       | N/A                    |
| `environments` | The target environment for deployment.| `choice`  | `testing`     | Yes      | `testing`, `staging`, `production` |

---

## Triggers

This workflow is triggered manually via the **`workflow_dispatch`** event in GitHub Actions. Users specify the branch hash and the target environment when initiating the workflow.

---

## Job Details

### Job: `deploy-unstable`

- **Runs on:** `ubuntu-latest`
- **Permissions:**
  - `contents: read`: To fetch repository contents.
  - `packages: write`: For updating deployment configurations.

#### Steps

1. **Deploy to Target Environment**
   - **Action Used:** `hathitrust/github_actions/deploy@v1`
   - **Inputs Passed to Action:**
     - `image`: Full image URL with branch hash (`ghcr.io/${{ github.repository }}:${{ inputs.branch_hash }}`).
     - `file`: Path to the environment-specific configuration file in the ArgoCD control repository (`environments/${{ github.event.repository.name }}/${{inputs.environments}}/web-image.txt`).
     - `CONFIG_REPO_RW_APP_ID`: Application ID for the configuration repository (from GitHub variables).
     - `CONFIG_REPO_FULL_NAME`: Full name of the configuration repository (from GitHub variables).
     - `CONFIG_REPO_RW_KEY`: Read/write key for accessing the configuration repository (from GitHub secrets).

---

## Notes

- **Environment Options:**
  - `testing`: For testing new features or changes.
  - `staging`: For pre-production validation.
  - `production`: For deploying the final, stable release.
- **ArgoCD Integration:** This workflow directly updates the `ht_tanka` ArgoCD control repository to reflect the specified image version and hash. This integration ensures seamless deployment.
- **Manual Execution:** Allows developers to precisely control deployments, reducing the risk of accidental releases.

---

## How to Use

1. Navigate to the **Actions** tab in your GitHub repository.
2. Select the **Deploy** workflow from the list.
3. Click **Run Workflow**.
4. Specify the following inputs:
   - `branch_hash`: The hash or branch name of the Docker image to deploy.
   - `environments`: Select one of the three environments (default is `testing`).
5. Click **Run Workflow** to start the deployment process.

---

## Example

### Triggering the Workflow for Deployment

- **branch_hash:** `abc1234` (example Git hash)
- **environments:** `staging`

This configuration will:
- Deploy the Docker image `ghcr.io/<repository>:abc1234` to the **staging** environment.
- Update the `ht_tanka` control repository file at `environments/<repository_name>/staging/web-image.txt` with the correct image URL and hash.

---

# Test Code Workflow

## Purpose

The workflow is designed to execute unit tests present in the project repository. It verifies that the code functions as expected and meets quality standards across multiple Python versions.

---

## Workflow Inputs

### Workflow Dispatch Inputs
| Input Name | Description                       | Type    | Default Value | Required |
|------------|-----------------------------------|---------|---------------|----------|
| `ref`      | Revision or branch to test.      | `string`| `main`        | No       |

### Workflow Call Inputs
| Input Name | Description                       | Type    | Default Value | Required |
|------------|-----------------------------------|---------|---------------|----------|
| `ref`      | Revision or branch to test.      | `string`| `main`        | Yes      |

---

## Triggers

- **Manual Trigger:** The workflow can be manually triggered using the **`workflow_dispatch`** event, allowing users to specify the branch or revision to test.
- **Reusable Workflow Trigger:** The **`workflow_call`** event allows other workflows to invoke this one and pass in the desired inputs.

---

## Job Details

### Job: `Test-Code`

- **Runs on:** `ubuntu-latest`
- 
---

## Notes
- **Customizability:** Users can modify the input `ref` to test different branches or revisions of the repository.
  
---

## How to Use

### Triggering the Workflow

1. Navigate to the **Actions** tab in your GitHub repository.
2. Select the **Run Tests on Code** workflow.
3. Click **Run Workflow**.
4. Specify the `ref` (branch or revision) to test (default is `main`).
5. Click **Run Workflow** to start the testing process.
---

## Example

### Triggering the Workflow Manually

- **ref:** `feature/new-api`

This configuration will:
- Test the branch `feature/new-api`.
  

#  Test Code Workflow
---

## Purpose

The workflow tests a specified Docker container image by executing custom test scripts or commands. This ensures the image meets quality standards before deployment. 

---

## Workflow Inputs

### Workflow Dispatch Inputs
| Input Name | Description                     | Type    | Default Value | Required |
|------------|---------------------------------|---------|---------------|----------|
| `ref`      | Revision or branch to test.    | `string`| `main`        | No       |
| `ghc_img`  | The GHCR.io image to test.     | `string`| None          | Yes      |

### Workflow Call Inputs
| Input Name | Description                     | Type    | Default Value | Required |
|------------|---------------------------------|---------|---------------|----------|
| `ref`      | Revision or branch to test.    | `string`| `main`        | Yes      |
| `ghc_img`  | The GHCR.io image to test.     | `string`| None          | Yes      |

---

## Triggers

- **Manual Trigger:** The workflow can be triggered manually via **`workflow_dispatch`**, allowing users to specify the branch and image to test.
- **Reusable Workflow Trigger:** It can also be invoked by other workflows via the **`workflow_call`** event, passing in the necessary inputs.

---

## Job Details

### Job: `Test-Image`

- **Runs on:** `ubuntu-latest`

#### Steps

- **Checkout Code:** Fetches the specified branch or revision for context during testing.
- **Run Container Tests:** Executes custom container tests using the provided image.

---

## Notes

- **Customizability:** This workflow serves as a template. Individual container tests can be defined within the job as per project requirements.
- **Docker Integration:** The workflow assumes the presence of Docker and uses commands like `docker run`, `docker exec`, and `docker stop` for container operations.

---

## How to Use

### Triggering the Workflow

1. Navigate to the **Actions** tab in your GitHub repository.
2. Select the **Run Tests on Container** workflow.
3. Click **Run Workflow**.
4. Specify the following inputs:
   - `ref`: The branch or revision to test (default is `main`).
   - `ghc_img`: The full GHCR.io image URL (e.g., `ghcr.io/<owner>/<repository>:<tag>`).
5. Click **Run Workflow** to start the container tests.

---

## Example

### Triggering the Workflow Manually

- **ref:** `feature/container-tests`
- **ghc_img:** `ghcr.io/example-repo/image:latest`

This configuration will:
- Test the container image `ghcr.io/example-repo/image:latest`.
- Use the branch `feature/container-tests` for any additional context required during the testing process.


# Tag Release Workflow
---

## Purpose

The workflow tags the latest Docker image built for the repository with a release version. This is triggered by GitHub release events and leverages the `v.*.*.*` tag format to align with semantic versioning conventions.

---

## Workflow Triggers

### Trigger: `release`
- **Event:** Fires when a release is published in the repository.
- **Release Types Monitored:**
  - `released`: Only triggers when a release is finalized.

---

## Job Details

### Job: `tag-release`

- **Runs on:** `ubuntu-latest`

#### Steps

1. **Tag Image**
   - **Action Used:** `hathitrust/github_actions/tag-release@v1`
   - **Inputs Passed to Action:**
     - `registry_token`: Authentication token to access GitHub Container Registry (`${{ github.token }}`).
     - `existing_tag`: The current tag of the Docker image being released (e.g., `ghcr.io/${{ github.repository }}:${{ github.sha }}`).
     - `image`: The base name of the Docker image (`ghcr.io/${{ github.repository }}`).
     - `new_tag`: The version tag extracted from the release event (`${{ github.event.release.tag_name }}`).

---

## How to Use

### Publishing a Release

1. Create a new release in the GitHub repository.
2. Provide a release version in the `v.*.*.*` format (e.g., `v1.2.3`).
3. Publish the release.
4. The workflow will:
   - Tag the latest Docker image associated with the repository and commit hash (`ghcr.io/<repository>:<sha>`).
   - Add the release version tag (`v1.2.3`) to the image.

---

## Example

### Release Workflow Example

If the repository has a Docker image tagged as `ghcr.io/example-repo:abc1234` and a release with the tag `v1.2.3` is published, this workflow will:
- Add the tag `v1.2.3` to the image.
- The image will now be accessible as `ghcr.io/example-repo:v1.2.3`.

---

## Notes

- Ensure that the release tags follow the `v.*.*.*` convention to prevent inconsistencies.

---
# CICD Pipeline Workflow

This GitHub Actions workflow is a complete CI/CD pipeline designed to streamline the process of testing, building, and deploying code to a production environment. The pipeline is triggered upon the creation of a new release with a specific tag, ensuring precise control over when code is deployed.

---

## Purpose

This workflow performs the following tasks in sequence:
1. Executes unit tests on the code.
2. Builds a Docker image from the repository.
3. Runs container-specific tests on the generated image.
4. Deploys the tested image to the specified environment, such as `testing`, `staging`, or `production`.

---

## Workflow Inputs

| Input Name    | Description                                   | Type       | Default Value          | Required |
|---------------|-----------------------------------------------|------------|------------------------|----------|
| `img_tag`     | Docker image tag for the build.              | `string`   | None                   | Yes      |
| `ref`         | Revision or branch to build.                 | `string`   | `main`                 | No       |
| `push_latest` | Indicates if the build should tag as `latest`.| `boolean`  | `false`                | No       |
| `platforms`   | Platforms to target for the build.           | `choice`   | `linux/amd64,linux/arm64` | No       |
| `environments`| Deployment environment (`testing`, `staging`, `production`).| `choice`   | `testing`              | No       |
| `rebuild`     | Indicates if the image should be rebuilt.    | `boolean`  | `false`                | No       |

---

## Triggers

- **Manual Trigger:** The workflow can be started manually with the `workflow_dispatch` event, allowing control over the build and deployment parameters.

---

## Notes

- **Hard-Coded Environment:** Currently, the environment is hard-coded as `testing`. This should be adjusted to align with the chosen deployment environment.
- **Sequential Execution:** The workflow ensures a proper CI/CD sequence, requiring tests and image validation before deployment.
- **Customizable Deployments:** Users can select the target environment (`testing`, `staging`, or `production`) for greater flexibility.

---

## How to Use

### Triggering the Workflow

1. Navigate to the **Actions** tab in your GitHub repository.
2. Select the **CICD Pipeline** workflow.
3. Click **Run Workflow**.
4. Specify the following inputs:
   - `img_tag`: The desired tag for the Docker image.
   - `ref`: The branch or revision to build.
   - `push_latest`: Whether to push the `latest` tag.
   - `platforms`: Target platforms for the image.
   - `environments`: Deployment environment.
   - `rebuild`: Whether to force rebuild the image.
5. Click **Run Workflow** to start the CI/CD process.
