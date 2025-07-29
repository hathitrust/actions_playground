# actions_playground
This repo is used to test out new or breaking changes to any actions workflow without disrupting the current configurations or packages that are deployed.

# Workflows
---

## Build
#### Purpose
This GitHub Action builds a Docker image using the specified branch or revision, with support for multiple platforms and optional rebuild and tagging behaviors.

#### Parameters
| Name| Type    | Description| Required | Default|
| ------ | ------- | ------ | -------- | -------- |
| `img_tag`     | string  | Docker image tag applied to the image | No      | –                         |
| `ref`         | string  | Git revision or branch to build from | No       | `main`                    |
| `push_latest` | boolean | Push the image tag as `latest` if `true` | No | `false`|
| `platforms`   | choice  | Supported platforms to build. `linux/amd64`, `linux/arm64` or both. | No | `linux/amd64,linux/arm64` |
| `rebuild`     | boolean | Force rebuild of the image           | No       | `false` |

#### Steps and Logic
| Step| Purpose|
| --------------- | ---------------------- |
| **Build Image** | Uses the[`hathitrust/github_actions/build@v1` 🔗](https://github.com/hathitrust/github_actions/blob/main/build/action.yml)  composite action to perform the Docker build and tagging. |


---

## Tag Image
#### Purpose
This GitHub Action is automatically triggered when a new GitHub release is published. It tags an existing Docker image (typically referenced by a commit SHA) with the corresponding release version tag (e.g., v1.2.3). This ensures the Docker registry reflects official release versions alongside commit-specific tags.

#### Parameters
| Name             | Type   | Description| Required | Default |
| ---------------- | ------ | -------------------- | -------- | ------- |
| `registry_token` | string | GitHub token used for authenticating with the container registry | No | GHA Token provided      |
| `existing_tag`   | string | The fully qualified reference to the existing image (e.g., SHA-based tag) | No | –       |
| `image`          | string | The Docker image repository to tag                                        | No | –       |
| `new_tag`        | string | The new tag to apply to the image (typically a GitHub release tag)        | No | –       |

#### Steps and Logic
| Step                                           | Purpose|
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **Tag Release** | Uses the action [`hathitrust/github_actions/tag-release\@v1` 🔗](https://github.com/hathitrust/github_actions/tree/main/tag-release) and applies a new release tag to an existing Docker image in the container registry (GHCR) and updates the `latest` tag accordingly. |
---

## Scan Image

#### Purpose
This GitHub Action scans a Docker image for vulnerabilities or security issues. It can be triggered manually and supports specifying a custom image reference and branch hash. Scan results can be used to assess image security prior to deployment or release.

#### Parameters
| Name| Type   | Description| Required | Default |
| ------------- | ------ | -------------------------- | -------- | ------- |
| `image-ref`   | string | The full image name to scan. If not provided, defaults to the latest image of this repository. | No       | –       |
| `branch_hash` | string | SHA or revision of the branch to scan (defaults to the triggering branch's SHA).               | No       | –       |

#### Steps and Logic
| Step| Purpose|
| --------------------------------------- | ----------------------------------------- |
| **Scanning Image** | Invokes the [`hathitrust/github_actions/scan-image@v1.7.0` 🔗](https://github.com/hathitrust/github_actions/tree/main/scan-image) action to perform a security scan on a Docker image using Trivy. |

---

## Deploy
#### Purpose
This GitHub Action is designed to deploy a Docker image to a specified environment (testing, staging, or production). The deployment is triggered manually via the workflow_dispatch event and supports specifying a custom branch hash or revision for deployment. The action interacts with the `ht_tanka` configuration repository to update environment deployment references within an applications `web-image.txt` file.

#### Parameters
| Name| Type   | Description| Required | Default   |
| -------------- | ------ | -------------------------- | -------- | --------- |
| `branch_hash`  | string | SHA or revision to deploy (defaults to the triggering branch SHA) | No       | –         |
| `environments` | choice | Target environment to deploy toOptions: `testing`, `staging`, `production` | No       | `testing` |

#### Steps and Logic
| Step| Purpose|
| --------------------------------------- | ----------------------------------------- |
| **Deploy to Environment** | Invokes the [`hathitrust/github_actions/deploy@v1` 🔗](https://github.com/hathitrust/github_actions/tree/main/deploy) action to update the deployment configuration for the specified environment. It writes the provided image reference to the appropriate environment file in the configuration repository and authenticates via a GitHub App. |
