# Context Learning Agent Training - Project Design Document

> Author: MSJ | Created: 2026-03-18

## 1. Core Insight

**Knowledge memorization is inefficient for small LLMs (4B-30B), but training context learning ability via agent trajectory data is both feasible and efficient.**

### The Problem

- Open-source projects like `huggingface_hub` update frequently; parameters get deprecated, APIs change
- Forcing LLMs to memorize specific API signatures into weights is:
  - **Low efficiency**: Parameter space is limited, knowledge density is poor
  - **Quick to decay**: Memorized APIs become outdated with each library release
  - **Hard to generalize**: Every new library requires re-training

### The Solution

Train models to **learn from context** rather than memorize knowledge:

1. **Explore** - Navigate project structure, find relevant files
2. **Extract** - Read source code, docs, type hints to understand current APIs
3. **Generate** - Produce code based on extracted context
4. **Verify** - Self-review by re-examining the project to validate generated code

This is a **meta-ability** that doesn't decay with API changes.

## 2. Key Observations

### 2.1 Context Learning > Parametric Memory

| Dimension | Parametric Memory | Context Learning |
|-----------|------------------|-----------------|
| Update cost | Retrain/fine-tune | Zero (reads live code) |
| Knowledge freshness | Stale after weeks | Always current |
| Generalization | Per-library | Cross-library |
| Model size requirement | Large | Small (4B+) |
| Verifiability | Hard | Easy (re-read source) |

### 2.2 Self-Verification is Tractable

The generation-verification asymmetry is key:
- **Generation** (writing code) is hard - many possible outputs
- **Verification** (reviewing code against source) is easier - binary correct/incorrect
- Even when generated code is wrong, the model can **act as a reviewer**, re-analyze the project, and detect errors **without executing the code**

### 2.3 Agent Trajectory Data as Training Signal

By constructing large-scale agent trajectories around popular open-source projects:
- The model learns **exploration patterns** (how to grep, read, navigate)
- The model learns **extraction patterns** (how to find relevant API info)
- The model learns **verification patterns** (how to cross-reference generated code with source)
- These patterns transfer across projects regardless of specific APIs

## 3. Training Strategy

### 3.1 Anchor Projects

Use popular, well-maintained open-source projects as "anchors" for trajectory generation. These projects serve as:

- **Diverse training environments** (different languages, structures, conventions)
- **Ground truth sources** (well-documented, well-tested code)
- **Difficulty gradients** (simple CLI tools → complex frameworks)

We have curated **3000 anchor projects** across 3 ecosystems:

| Ecosystem | Count | Categories | Notes |
|-----------|-------|------------|-------|
| CLI Tools | 1000 | 20 | 27 languages, Go/C/Rust dominant |
| Python Packages | 1000 | 136 | Web, ML, NLP, CV, data, DevOps, etc. |
| JS/TS Packages | 1000 | 123 | Frameworks, bundlers, UI, state, etc. |

### 3.2 Trajectory Data Construction

For each anchor project, generate multiple agent trajectories:

```
Task: "Use {library} to {specific_task}"
     ↓
Agent Trajectory:
  1. [EXPLORE] List project structure → find relevant modules
  2. [READ] Read source files, docstrings, type hints
  3. [EXTRACT] Identify current API signatures and patterns
  4. [GENERATE] Write code using extracted knowledge
  5. [VERIFY] Re-read source to validate generated code
  6. [CORRECT] Fix issues found during verification
```

### 3.3 Training Phases

**Phase 1: Basic Navigation**
- File search (grep, find, glob patterns)
- Code reading and comprehension
- Project structure understanding

**Phase 2: API Extraction**
- Finding function signatures, class definitions
- Understanding deprecated vs current APIs
- Reading type annotations and docstrings

**Phase 3: Code Generation with Context**
- Generating code that uses current APIs correctly
- Handling edge cases based on source code reading
- Following project-specific conventions

**Phase 4: Self-Verification**
- Cross-referencing generated code against source
- Detecting incorrect API usage, missing parameters
- Proposing corrections based on verification results

### 3.4 Data Quality Principles

- **Quality >> Quantity**: Bad trajectories teach wrong exploration patterns
- **Synthetic + Real**: Use real project trajectories as skeleton, synthesize variants
- **Contrastive Learning**: Include both success and failure trajectories (e.g., using deprecated APIs)
- **Diversity**: Vary project structure, language, documentation style, API complexity

## 4. Expected Outcomes

A fine-tuned model (4B-30B) with strong context learning should be able to:

1. **Navigate any codebase** - Not just the 3000 training anchors
2. **Use any library correctly** - By reading its source, not memorizing its APIs
3. **Self-verify without execution** - Catch errors through code review
4. **Stay current** - Works with latest APIs without retraining
5. **Handle private/internal code** - The skill transfers to non-public repositories

## 5. Challenges & Mitigations

| Challenge | Mitigation |
|-----------|------------|
| Trajectory quality control | Automated validation + human review pipeline |
| Generalization to cold/private projects | Maximize structural diversity in training |
| Context window limits (small models) | Train efficient exploration strategies (minimize reads) |
| Evaluation benchmark design | Create held-out project set with version-specific tasks |
| Compute cost for trajectory generation | Prioritize high-value projects, use cheaper models for drafts |

## 6. Anchor Project Statistics

### 6.1 CLI Tools Overview

- **1000 projects** across **20 categories**
- **27 programming languages** represented
- Top languages: Go (318), C (245), Rust (155), Python (83), C++ (68)
- Top categories: system (96), security (87), network (81), file-management (72), misc (70), build-tool (63)

### 6.2 Python Packages Overview

- **1000 projects** across **136 categories**
- Top categories: testing (57), web-framework (28), database (23), utilities (23), ml (21), nlp (21), django (21), packaging (20), web-utils (20), api (17)

### 6.3 JS/TS Packages Overview

- **1000 projects** across **123 categories**
- Top categories: utility (88), mobile (45), server (38), testing (38), devtools (25), component (25), cli (23), vue-ecosystem (22), database (21), graphql (21)

---

## 7. Full Project Lists

> Data files: `data/cli_tools.json`, `data/python_packages.json`, `data/js_ts_packages.json`

### CLI Tools (1000 projects, 20 categories)

| # | Name | Repo | Category | Language |
|---|------|------|----------|----------|
| 1 | git | `git/git` | version-control | C |
| 2 | curl | `curl/curl` | network | C |
| 3 | wget | `mirror/wget` | network | C |
| 4 | docker | `moby/moby` | container | Go |
| 5 | kubectl | `kubernetes/kubernetes` | container | Go |
| 6 | terraform | `hashicorp/terraform` | devops | Go |
| 7 | ansible | `ansible/ansible` | devops | Python |
| 8 | ripgrep | `BurntSushi/ripgrep` | search | Rust |
| 9 | fd | `sharkdp/fd` | search | Rust |
| 10 | bat | `sharkdp/bat` | file-management | Rust |
| 11 | eza | `eza-community/eza` | file-management | Rust |
| 12 | fzf | `junegunn/fzf` | search | Go |
| 13 | tmux | `tmux/tmux` | shell | C |
| 14 | htop | `htop-dev/htop` | monitoring | C |
| 15 | jq | `jqlang/jq` | file-management | C |
| 16 | yq | `mikefarah/yq` | file-management | Go |
| 17 | gh | `cli/cli` | version-control | Go |
| 18 | aws-cli | `aws/aws-cli` | cloud | Python |
| 19 | gcloud | `google-cloud-sdk` | cloud | Python |
| 20 | az | `Azure/azure-cli` | cloud | Python |
| 21 | helm | `helm/helm` | container | Go |
| 22 | nginx | `nginx/nginx` | network | C |
| 23 | redis-cli | `redis/redis` | database | C |
| 24 | psql | `postgres/postgres` | database | C |
| 25 | mysql | `mysql/mysql-server` | database | C++ |
| 26 | sqlite3 | `sqlite/sqlite` | database | C |
| 27 | ffmpeg | `FFmpeg/FFmpeg` | media | C |
| 28 | imagemagick | `ImageMagick/ImageMagick` | media | C |
| 29 | pandoc | `jgm/pandoc` | file-management | Haskell |
| 30 | hugo | `gohugoio/hugo` | build-tool | Go |
| 31 | neovim | `neovim/neovim` | editor | C |
| 32 | zsh | `zsh-users/zsh` | shell | C |
| 33 | fish | `fish-shell/fish-shell` | shell | Rust |
| 34 | starship | `starship/starship` | shell | Rust |
| 35 | zoxide | `ajeetdsouza/zoxide` | shell | Rust |
| 36 | atuin | `atuinsh/atuin` | shell | Rust |
| 37 | lazygit | `jesseduffield/lazygit` | version-control | Go |
| 38 | lazydocker | `jesseduffield/lazydocker` | container | Go |
| 39 | k9s | `derailed/k9s` | container | Go |
| 40 | stern | `stern/stern` | container | Go |
| 41 | argocd | `argoproj/argo-cd` | devops | Go |
| 42 | vault | `hashicorp/vault` | security | Go |
| 43 | consul | `hashicorp/consul` | devops | Go |
| 44 | nmap | `nmap/nmap` | security | C |
| 45 | tshark | `wireshark/wireshark` | network | C |
| 46 | httpie | `httpie/cli` | network | Python |
| 47 | hey | `rakyll/hey` | testing | Go |
| 48 | wrk | `wg/wrk` | testing | C |
| 49 | vegeta | `tsenart/vegeta` | testing | Go |
| 50 | grpcurl | `fullstorydev/grpcurl` | network | Go |
| 51 | protoc | `protocolbuffers/protobuf` | build-tool | C++ |
| 52 | make | `mirror/make` | build-tool | C |
| 53 | cmake | `Kitware/CMake` | build-tool | C++ |
| 54 | ninja | `ninja-build/ninja` | build-tool | C++ |
| 55 | bazel | `bazelbuild/bazel` | build-tool | Java |
| 56 | gradle | `gradle/gradle` | build-tool | Java |
| 57 | maven | `apache/maven` | build-tool | Java |
| 58 | cargo | `rust-lang/cargo` | package-manager | Rust |
| 59 | rustup | `rust-lang/rustup` | package-manager | Rust |
| 60 | go | `golang/go` | build-tool | Go |
| 61 | deno | `denoland/deno` | build-tool | Rust |
| 62 | bun | `oven-sh/bun` | build-tool | Zig |
| 63 | pnpm | `pnpm/pnpm` | package-manager | TypeScript |
| 64 | yarn | `yarnpkg/berry` | package-manager | TypeScript |
| 65 | npm | `npm/cli` | package-manager | JavaScript |
| 66 | pip | `pypa/pip` | package-manager | Python |
| 67 | pipx | `pypa/pipx` | package-manager | Python |
| 68 | poetry | `python-poetry/poetry` | package-manager | Python |
| 69 | pdm | `pdm-project/pdm` | package-manager | Python |
| 70 | uv | `astral-sh/uv` | package-manager | Rust |
| 71 | ruff | `astral-sh/ruff` | linter | Rust |
| 72 | black | `psf/black` | formatter | Python |
| 73 | prettier | `prettier/prettier` | formatter | JavaScript |
| 74 | eslint | `eslint/eslint` | linter | JavaScript |
| 75 | shellcheck | `koalaman/shellcheck` | linter | Haskell |
| 76 | hadolint | `hadolint/hadolint` | linter | Haskell |
| 77 | trivy | `aquasecurity/trivy` | security | Go |
| 78 | snyk | `snyk/cli` | security | TypeScript |
| 79 | semgrep | `semgrep/semgrep` | security | OCaml |
| 80 | sonar-scanner | `SonarSource/sonar-scanner-cli` | linter | Java |
| 81 | act | `nektos/act` | devops | Go |
| 82 | direnv | `direnv/direnv` | shell | Go |
| 83 | asdf | `asdf-vm/asdf` | package-manager | Shell |
| 84 | mise | `jdx/mise` | package-manager | Rust |
| 85 | nvm | `nvm-sh/nvm` | package-manager | Shell |
| 86 | pyenv | `pyenv/pyenv` | package-manager | Shell |
| 87 | rbenv | `rbenv/rbenv` | package-manager | Shell |
| 88 | tfenv | `tfutils/tfenv` | package-manager | Shell |
| 89 | just | `casey/just` | build-tool | Rust |
| 90 | task | `go-task/task` | build-tool | Go |
| 91 | watchexec | `watchexec/watchexec` | system | Rust |
| 92 | entr | `eradman/entr` | system | C |
| 93 | mkcert | `FiloSottile/mkcert` | security | Go |
| 94 | step-cli | `smallstep/cli` | security | Go |
| 95 | age | `FiloSottile/age` | security | Go |
| 96 | sops | `getsops/sops` | security | Go |
| 97 | gpg | `gpg/gnupg` | security | C |
| 98 | openssh | `openssh/openssh-portable` | network | C |
| 99 | rsync | `RsyncProject/rsync` | file-management | C |
| 100 | rclone | `rclone/rclone` | file-management | Go |
| 101 | restic | `restic/restic` | file-management | Go |
| 102 | borgbackup | `borgbackup/borg` | file-management | Python |
| 103 | dust | `bootandy/dust` | system | Rust |
| 104 | duf | `muesli/duf` | system | Go |
| 105 | procs | `dalance/procs` | system | Rust |
| 106 | bottom | `ClementTsang/bottom` | monitoring | Rust |
| 107 | glances | `nicolargo/glances` | monitoring | Python |
| 108 | bandwhich | `imsnif/bandwhich` | monitoring | Rust |
| 109 | dog | `ogham/dog` | network | Rust |
| 110 | xh | `ducaale/xh` | network | Rust |
| 111 | grex | `pemistahl/grex` | misc | Rust |
| 112 | sd | `chmln/sd` | search | Rust |
| 113 | choose | `theryangeary/choose` | misc | Rust |
| 114 | delta | `dandavison/delta` | version-control | Rust |
| 115 | difftastic | `Wilfred/difftastic` | version-control | Rust |
| 116 | tokei | `XAMPPRocky/tokei` | misc | Rust |
| 117 | scc | `boyter/scc` | misc | Go |
| 118 | hyperfine | `sharkdp/hyperfine` | testing | Rust |
| 119 | pueue | `Nukesor/pueue` | system | Rust |
| 120 | zellij | `zellij-org/zellij` | shell | Rust |
| 121 | wezterm | `wez/wezterm` | shell | Rust |
| 122 | alacritty | `alacritty/alacritty` | shell | Rust |
| 123 | kitty | `kovidgoyal/kitty` | shell | Python |
| 124 | mosh | `mobile-shell/mosh` | network | C++ |
| 125 | caddy | `caddyserver/caddy` | network | Go |
| 126 | traefik | `traefik/traefik` | network | Go |
| 127 | mc | `minio/mc` | cloud | Go |
| 128 | etcdctl | `etcd-io/etcd` | database | Go |
| 129 | flyctl | `superfly/flyctl` | cloud | Go |
| 130 | doctl | `digitalocean/doctl` | cloud | Go |
| 131 | linode-cli | `linode/linode-cli` | cloud | Python |
| 132 | hcloud | `hetznercloud/cli` | cloud | Go |
| 133 | eksctl | `eksctl-io/eksctl` | container | Go |
| 134 | kind | `kubernetes-sigs/kind` | container | Go |
| 135 | minikube | `kubernetes/minikube` | container | Go |
| 136 | k3s | `k3s-io/k3s` | container | Go |
| 137 | k3d | `k3d-io/k3d` | container | Go |
| 138 | skaffold | `GoogleContainerTools/skaffold` | devops | Go |
| 139 | pulumi | `pulumi/pulumi` | devops | Go |
| 140 | crossplane | `crossplane/crossplane` | devops | Go |
| 141 | copilot-cli | `aws/copilot-cli` | cloud | Go |
| 142 | sam-cli | `aws/aws-sam-cli` | cloud | Python |
| 143 | serverless | `serverless/serverless` | devops | JavaScript |
| 144 | wrangler | `cloudflare/workers-sdk` | cloud | TypeScript |
| 145 | netlify-cli | `netlify/cli` | cloud | JavaScript |
| 146 | vercel-cli | `vercel/vercel` | cloud | TypeScript |
| 147 | firebase-cli | `firebase/firebase-tools` | cloud | TypeScript |
| 148 | supabase-cli | `supabase/cli` | cloud | Go |
| 149 | planetscale-cli | `planetscale/cli` | database | Go |
| 150 | turso-cli | `tursodatabase/turso-cli` | database | Go |
| 151 | neon-cli | `neondatabase/neonctl` | database | TypeScript |
| 152 | mongosh | `mongodb-js/mongosh` | database | TypeScript |
| 153 | clickhouse-client | `ClickHouse/ClickHouse` | database | C++ |
| 154 | duckdb | `duckdb/duckdb` | database | C++ |
| 155 | usql | `xo/usql` | database | Go |
| 156 | pgcli | `dbcli/pgcli` | database | Python |
| 157 | mycli | `dbcli/mycli` | database | Python |
| 158 | litecli | `dbcli/litecli` | database | Python |
| 159 | iredis | `laixintao/iredis` | database | Python |
| 160 | posting | `darrenburns/posting` | network | Python |
| 161 | slides | `maaslalani/slides` | misc | Go |
| 162 | glow | `charmbracelet/glow` | misc | Go |
| 163 | vhs | `charmbracelet/vhs` | misc | Go |
| 164 | gum | `charmbracelet/gum` | shell | Go |
| 165 | nushell | `nushell/nushell` | shell | Rust |
| 166 | helix | `helix-editor/helix` | editor | Rust |
| 167 | micro | `zyedidia/micro` | editor | Go |
| 168 | kakoune | `mawww/kakoune` | editor | C++ |
| 169 | vim | `vim/vim` | editor | C |
| 170 | emacs | `emacs-mirror/emacs` | editor | C |
| 171 | tree-sitter | `tree-sitter/tree-sitter` | build-tool | Rust |
| 172 | ctags | `universal-ctags/ctags` | editor | C |
| 173 | lf | `gokcehan/lf` | file-management | Go |
| 174 | ranger | `ranger/ranger` | file-management | Python |
| 175 | yazi | `sxyazi/yazi` | file-management | Rust |
| 176 | broot | `Canop/broot` | file-management | Rust |
| 177 | nnn | `jarun/nnn` | file-management | C |
| 178 | tree | `Old-Man-Programmer/tree` | file-management | C |
| 179 | aria2 | `aria2/aria2` | network | C++ |
| 180 | yt-dlp | `yt-dlp/yt-dlp` | media | Python |
| 181 | pass | `zx2c4/password-store` | security | Shell |
| 182 | gopass | `gopasspw/gopass` | security | Go |
| 183 | bitwarden-cli | `bitwarden/clients` | security | TypeScript |
| 184 | chezmoi | `twpayne/chezmoi` | file-management | Go |
| 185 | ab | `apache/httpd` | testing | C |
| 186 | siege | `JoeDog/siege` | testing | C |
| 187 | k6 | `grafana/k6` | testing | Go |
| 188 | podman | `containers/podman` | container | Go |
| 189 | dive | `wagoodman/dive` | container | Go |
| 190 | cosign | `sigstore/cosign` | security | Go |
| 191 | flux | `fluxcd/flux2` | devops | Go |
| 192 | kustomize | `kubernetes-sigs/kustomize` | devops | Go |
| 193 | istioctl | `istio/istio` | network | Go |
| 194 | prometheus | `prometheus/prometheus` | monitoring | Go |
| 195 | grafana-cli | `grafana/grafana` | monitoring | Go |
| 196 | loki | `grafana/loki` | monitoring | Go |
| 197 | vector | `vectordotdev/vector` | monitoring | Rust |
| 198 | tmate | `tmate-io/tmate` | shell | C |
| 199 | asciinema | `asciinema/asciinema` | misc | Rust |
| 200 | cloc | `AlDanial/cloc` | misc | Perl |
| 201 | stow | `aspiers/stow` | file-management | Perl |
| 202 | tig | `jonas/tig` | version-control | C |
| 203 | gitui | `extrawurst/gitui` | version-control | Rust |
| 204 | onefetch | `o2sh/onefetch` | version-control | Rust |
| 205 | git-cliff | `orhun/git-cliff` | version-control | Rust |
| 206 | cocogitto | `cocogitto/cocogitto` | version-control | Rust |
| 207 | commitizen | `commitizen-tools/commitizen` | version-control | Python |
| 208 | pre-commit | `pre-commit/pre-commit` | linter | Python |
| 209 | lefthook | `evilmartians/lefthook` | version-control | Go |
| 210 | sshuttle | `sshuttle/sshuttle` | network | Python |
| 211 | tailscale | `tailscale/tailscale` | network | Go |
| 212 | nebula | `slackhq/nebula` | network | Go |
| 213 | zerotier-cli | `zerotier/ZeroTierOne` | network | C++ |
| 214 | socat | `3ndG4me/socat` | network | C |
| 215 | tcpdump | `the-tcpdump-group/tcpdump` | network | C |
| 216 | iperf3 | `esnet/iperf` | network | C |
| 217 | mtr | `traviscross/mtr` | network | C |
| 218 | haproxy | `haproxy/haproxy` | network | C |
| 219 | envoy | `envoyproxy/envoy` | network | C++ |
| 220 | linkerd-cli | `linkerd/linkerd2` | network | Go |
| 221 | cilium-cli | `cilium/cilium-cli` | network | Go |
| 222 | cert-manager | `cert-manager/cert-manager` | security | Go |
| 223 | external-dns | `kubernetes-sigs/external-dns` | devops | Go |
| 224 | certbot | `certbot/certbot` | security | Python |
| 225 | acme.sh | `acmesh-official/acme.sh` | security | Shell |
| 226 | openssl | `openssl/openssl` | security | C |
| 227 | cfssl | `cloudflare/cfssl` | security | Go |
| 228 | minisign | `jedisct1/minisign` | security | C |
| 229 | notation | `notaryproject/notation` | security | Go |
| 230 | oras | `oras-project/oras` | container | Go |
| 231 | crane | `google/go-containerregistry` | container | Go |
| 232 | skopeo | `containers/skopeo` | container | Go |
| 233 | buildah | `containers/buildah` | container | Go |
| 234 | kaniko | `GoogleContainerTools/kaniko` | container | Go |
| 235 | earthly | `earthly/earthly` | build-tool | Go |
| 236 | dagger | `dagger/dagger` | devops | Go |
| 237 | pack | `buildpacks/pack` | container | Go |
| 238 | grype | `anchore/grype` | security | Go |
| 239 | syft | `anchore/syft` | security | Go |
| 240 | falco | `falcosecurity/falco` | security | C++ |
| 241 | tetragon | `cilium/tetragon` | security | Go |
| 242 | kubescape | `kubescape/kubescape` | security | Go |
| 243 | kyverno | `kyverno/kyverno` | security | Go |
| 244 | opa | `open-policy-agent/opa` | security | Go |
| 245 | polaris | `FairwindsOps/polaris` | security | Go |
| 246 | checkov | `bridgecrewio/checkov` | security | Python |
| 247 | tfsec | `aquasecurity/tfsec` | security | Go |
| 248 | terrascan | `tenable/terrascan` | security | Go |
| 249 | infracost | `infracost/infracost` | devops | Go |
| 250 | tflint | `terraform-linters/tflint` | linter | Go |
| 251 | steampipe | `turbot/steampipe` | database | Go |
| 252 | cloudquery | `cloudquery/cloudquery` | cloud | Go |
| 253 | osquery | `osquery/osquery` | monitoring | C++ |
| 254 | velero | `vmware-tanzu/velero` | devops | Go |
| 255 | longhorn | `longhorn/longhorn` | devops | Go |
| 256 | minio | `minio/minio` | cloud | Go |
| 257 | litestream | `benbjohnson/litestream` | database | Go |
| 258 | pgbackrest | `pgbackrest/pgbackrest` | database | C |
| 259 | wal-g | `wal-g/wal-g` | database | Go |
| 260 | temporal-cli | `temporalio/cli` | devops | Go |
| 261 | dapr | `dapr/cli` | devops | Go |
| 262 | wasmtime | `bytecodealliance/wasmtime` | build-tool | Rust |
| 263 | wasmer | `wasmerio/wasmer` | build-tool | Rust |
| 264 | zig | `ziglang/zig` | build-tool | Zig |
| 265 | gleam | `gleam-lang/gleam` | build-tool | Rust |
| 266 | elixir | `elixir-lang/elixir` | build-tool | Elixir |
| 267 | ocaml | `ocaml/ocaml` | build-tool | OCaml |
| 268 | opam | `ocaml/opam` | package-manager | OCaml |
| 269 | dune | `ocaml/dune` | build-tool | OCaml |
| 270 | cabal | `haskell/cabal` | package-manager | Haskell |
| 271 | stack | `commercialhaskell/stack` | build-tool | Haskell |
| 272 | nix | `NixOS/nix` | package-manager | C++ |
| 273 | homebrew | `Homebrew/brew` | package-manager | Ruby |
| 274 | scoop | `ScoopInstaller/Scoop` | package-manager | PowerShell |
| 275 | chocolatey | `chocolatey/choco` | package-manager | C# |
| 276 | flatpak | `flatpak/flatpak` | package-manager | C |
| 277 | snap | `snapcore/snapd` | package-manager | Go |
| 278 | gitmux | `arl/gitmux` | version-control | Go |
| 279 | git-lfs | `git-lfs/git-lfs` | version-control | Go |
| 280 | git-secret | `sobolevn/git-secret` | security | Shell |
| 281 | git-crypt | `AGWA/git-crypt` | security | C++ |
| 282 | git-filter-repo | `newren/git-filter-repo` | version-control | Python |
| 283 | git-absorb | `tummychow/git-absorb` | version-control | Rust |
| 284 | git-branchless | `arxanas/git-branchless` | version-control | Rust |
| 285 | git-interactive-rebase-tool | `MitMaro/git-interactive-rebase-tool` | version-control | Rust |
| 286 | glab | `profclems/glab` | version-control | Go |
| 287 | saml2aws | `Versent/saml2aws` | cloud | Go |
| 288 | chamber | `segmentio/chamber` | security | Go |
| 289 | aws-vault | `99designs/aws-vault` | cloud | Go |
| 290 | granted | `common-fate/granted` | cloud | Go |
| 291 | terragrunt | `gruntwork-io/terragrunt` | devops | Go |
| 292 | atlantis | `runatlantis/atlantis` | devops | Go |
| 293 | packer | `hashicorp/packer` | devops | Go |
| 294 | vagrant | `hashicorp/vagrant` | devops | Ruby |
| 295 | nomad | `hashicorp/nomad` | devops | Go |
| 296 | boundary | `hashicorp/boundary` | security | Go |
| 297 | waypoint | `hashicorp/waypoint` | devops | Go |
| 298 | teleport | `gravitational/teleport` | security | Go |
| 299 | age-keygen | `FiloSottile/age` | security | Go |
| 300 | kubectl-neat | `itaysk/kubectl-neat` | container | Go |
| 301 | kubectx | `ahmetb/kubectx` | container | Go |
| 302 | kubeseal | `bitnami-labs/sealed-secrets` | security | Go |
| 303 | krew | `kubernetes-sigs/krew` | container | Go |
| 304 | popeye | `derailed/popeye` | container | Go |
| 305 | kubeshark | `kubeshark/kubeshark` | container | Go |
| 306 | kubebuilder | `kubernetes-sigs/kubebuilder` | build-tool | Go |
| 307 | operator-sdk | `operator-framework/operator-sdk` | build-tool | Go |
| 308 | cilium | `cilium/cilium` | network | Go |
| 309 | calicoctl | `projectcalico/calico` | network | Go |
| 310 | coredns | `coredns/coredns` | network | Go |
| 311 | wtfutil | `wtfutil/wtf` | monitoring | Go |
| 312 | sampler | `sqshq/sampler` | monitoring | Go |
| 313 | ctop | `bcicen/ctop` | container | Go |
| 314 | dry | `moncho/dry` | container | Go |
| 315 | buildkit | `moby/buildkit` | container | Go |
| 316 | nerdctl | `containerd/nerdctl` | container | Go |
| 317 | containerd | `containerd/containerd` | container | Go |
| 318 | cri-tools | `kubernetes-sigs/cri-tools` | container | Go |
| 319 | tilt | `tilt-dev/tilt` | devops | Go |
| 320 | devspace | `devspace-sh/devspace` | devops | Go |
| 321 | garden | `garden-io/garden` | devops | TypeScript |
| 322 | okteto | `okteto/okteto` | devops | Go |
| 323 | telepresence | `telepresenceio/telepresence` | devops | Go |
| 324 | goreleaser | `goreleaser/goreleaser` | build-tool | Go |
| 325 | ko | `ko-build/ko` | build-tool | Go |
| 326 | buf | `bufbuild/buf` | build-tool | Go |
| 327 | golangci-lint | `golangci/golangci-lint` | linter | Go |
| 328 | staticcheck | `dominikh/go-tools` | linter | Go |
| 329 | clippy | `rust-lang/rust-clippy` | linter | Rust |
| 330 | rustfmt | `rust-lang/rustfmt` | formatter | Rust |
| 331 | taplo | `tamasfe/taplo` | formatter | Rust |
| 332 | stylua | `JohnnyMorganz/StyLua` | formatter | Rust |
| 333 | dprint | `dprint/dprint` | formatter | Rust |
| 334 | biome | `biomejs/biome` | linter | Rust |
| 335 | oxlint | `oxc-project/oxc` | linter | Rust |
| 336 | yamllint | `adrienverge/yamllint` | linter | Python |
| 337 | actionlint | `rhysd/actionlint` | linter | Go |
| 338 | markdownlint-cli | `igorshubovych/markdownlint-cli` | linter | JavaScript |
| 339 | vale | `errata-ai/vale` | linter | Go |
| 340 | typos | `crate-ci/typos` | linter | Rust |
| 341 | cspell | `streetsidesoftware/cspell` | linter | TypeScript |
| 342 | shfmt | `mvdan/sh` | formatter | Go |
| 343 | gofmt | `golang/go` | formatter | Go |
| 344 | isort | `PyCQA/isort` | formatter | Python |
| 345 | autopep8 | `hhatto/autopep8` | formatter | Python |
| 346 | mypy | `python/mypy` | linter | Python |
| 347 | pyright | `microsoft/pyright` | linter | TypeScript |
| 348 | pylint | `pylint-dev/pylint` | linter | Python |
| 349 | flake8 | `PyCQA/flake8` | linter | Python |
| 350 | bandit | `PyCQA/bandit` | security | Python |
| 351 | safety | `pyupio/safety` | security | Python |
| 352 | pytest | `pytest-dev/pytest` | testing | Python |
| 353 | tox | `tox-dev/tox` | testing | Python |
| 354 | nox | `wntrblm/nox` | testing | Python |
| 355 | jest | `jestjs/jest` | testing | TypeScript |
| 356 | vitest | `vitest-dev/vitest` | testing | TypeScript |
| 357 | playwright | `microsoft/playwright` | testing | TypeScript |
| 358 | cypress | `cypress-io/cypress` | testing | JavaScript |
| 359 | locust | `locustio/locust` | testing | Python |
| 360 | gatling | `gatling/gatling` | testing | Scala |
| 361 | artillery | `artilleryio/artillery` | testing | JavaScript |
| 362 | plow | `six-ddc/plow` | testing | Go |
| 363 | oha | `hatoo/oha` | testing | Rust |
| 364 | bombardier | `codesenberg/bombardier` | testing | Go |
| 365 | mkcert-dev | `nicedoc/mkcert` | security | JavaScript |
| 366 | gitleaks | `gitleaks/gitleaks` | security | Go |
| 367 | trufflehog | `trufflesecurity/trufflehog` | security | Go |
| 368 | detect-secrets | `Yelp/detect-secrets` | security | Python |
| 369 | talisman | `thoughtworks/talisman` | security | Go |
| 370 | kube-bench | `aquasecurity/kube-bench` | security | Go |
| 371 | kube-hunter | `aquasecurity/kube-hunter` | security | Python |
| 372 | nuclei | `projectdiscovery/nuclei` | security | Go |
| 373 | subfinder | `projectdiscovery/subfinder` | security | Go |
| 374 | httpx-pd | `projectdiscovery/httpx` | security | Go |
| 375 | masscan | `robertdavidgraham/masscan` | security | C |
| 376 | zmap | `zmap/zmap` | security | C |
| 377 | lynis | `CISOfy/lynis` | security | Shell |
| 378 | clamav | `Cisco-Talos/clamav` | security | Rust |
| 379 | pixie | `pixie-io/pixie` | monitoring | C++ |
| 380 | jaeger | `jaegertracing/jaeger` | monitoring | Go |
| 381 | tempo | `grafana/tempo` | monitoring | Go |
| 382 | thanos | `thanos-io/thanos` | monitoring | Go |
| 383 | cortex | `cortexproject/cortex` | monitoring | Go |
| 384 | promtail | `grafana/loki` | monitoring | Go |
| 385 | fluentbit | `fluent/fluent-bit` | monitoring | C |
| 386 | filebeat | `elastic/beats` | monitoring | Go |
| 387 | logcli | `grafana/loki` | monitoring | Go |
| 388 | mprocs | `pvolok/mprocs` | system | Rust |
| 389 | process-compose | `F1bonacc1/process-compose` | system | Go |
| 390 | overmind | `DarthSim/overmind` | system | Go |
| 391 | foreman | `ddollar/foreman` | system | Ruby |
| 392 | honcho | `nickstenning/honcho` | system | Python |
| 393 | supervisor | `Supervisor/supervisor` | system | Python |
| 394 | monit | `arnoldsson/monit` | monitoring | C |
| 395 | croc | `schollz/croc` | file-management | Go |
| 396 | magic-wormhole | `magic-wormhole/magic-wormhole` | file-management | Python |
| 397 | syncthing | `syncthing/syncthing` | file-management | Go |
| 398 | age-plugin-yubikey | `str4d/age-plugin-yubikey` | security | Rust |
| 399 | viddy | `sachaos/viddy` | system | Go |
| 400 | topgrade | `topgrade-rs/topgrade` | system | Rust |
| 401 | awk | `onetrueawk/awk` | search | C |
| 402 | sed | `mirror/sed` | search | C |
| 403 | perl | `Perl/perl5` | shell | C |
| 404 | cut | `coreutils/coreutils` | search | C |
| 405 | sort | `coreutils/coreutils` | search | C |
| 406 | uniq | `coreutils/coreutils` | search | C |
| 407 | tr | `coreutils/coreutils` | search | C |
| 408 | wc | `coreutils/coreutils` | search | C |
| 409 | comm | `coreutils/coreutils` | search | C |
| 410 | paste | `coreutils/coreutils` | search | C |
| 411 | join | `coreutils/coreutils` | search | C |
| 412 | csplit | `coreutils/coreutils` | search | C |
| 413 | split | `coreutils/coreutils` | file-management | C |
| 414 | tee | `coreutils/coreutils` | shell | C |
| 415 | gzip | `madler/zlib` | file-management | C |
| 416 | bzip2 | `dsnet/compress` | file-management | C |
| 417 | xz | `tukaani-project/xz` | file-management | C |
| 418 | zstd | `facebook/zstd` | file-management | C |
| 419 | lz4 | `lz4/lz4` | file-management | C |
| 420 | pigz | `madler/pigz` | file-management | C |
| 421 | pbzip2 | `ruanhuabin/pbzip2` | file-management | C++ |
| 422 | tar | `gnu-mirror/tar` | file-management | C |
| 423 | zip | `infozip/zip` | file-management | C |
| 424 | unzip | `infozip/unzip` | file-management | C |
| 425 | 7z | `ip7z/7zip` | file-management | C++ |
| 426 | unrar | `aawc/unrar` | file-management | C++ |
| 427 | cpio | `gnu-mirror/cpio` | file-management | C |
| 428 | ncdu | `rofl0r/ncdu` | system | Zig |
| 429 | gdu | `dundee/gdu` | system | Go |
| 430 | fswatch | `emcrisostomo/fswatch` | file-management | C++ |
| 431 | inotifywait | `inotify-tools/inotify-tools` | file-management | C |
| 432 | lsof | `lsof-org/lsof` | system | C |
| 433 | fuser | `psmisc/psmisc` | system | C |
| 434 | sshfs | `libfuse/sshfs` | file-management | C |
| 435 | systemctl | `systemd/systemd` | system | C |
| 436 | supervisord | `Supervisor/supervisor` | system | Python |
| 437 | pm2 | `Unitech/pm2` | system | JavaScript |
| 438 | nodemon | `remy/nodemon` | misc | JavaScript |
| 439 | concurrently | `open-cli-tools/concurrently` | misc | TypeScript |
| 440 | goreman | `mattn/goreman` | system | Go |
| 441 | screen | `gnu-mirror/screen` | shell | C |
| 442 | byobu | `dustinkirkland/byobu` | shell | Shell |
| 443 | abduco | `martanne/abduco` | shell | C |
| 444 | dtach | `crispy1989/dtach` | shell | C |
| 445 | reptyr | `nelhage/reptyr` | shell | C |
| 446 | iptables | `netfilter/iptables` | network | C |
| 447 | nftables | `netfilter/nftables` | network | C |
| 448 | ufw | `jbq/ufw` | network | Python |
| 449 | fail2ban | `fail2ban/fail2ban` | security | Python |
| 450 | crowdsec | `crowdsecurity/crowdsec` | security | Go |
| 451 | suricata | `OISF/suricata` | security | C |
| 452 | snort | `snort3/snort3` | security | C++ |
| 453 | zeek | `zeek/zeek` | security | C++ |
| 454 | vnstat | `vergoh/vnstat` | network | C |
| 455 | nethogs | `raboof/nethogs` | network | C++ |
| 456 | iftop | `pdw/iftop` | network | C |
| 457 | nload | `rolandriegel/nload` | network | C++ |
| 458 | bmon | `tgraf/bmon` | network | C |
| 459 | speedtest-cli | `sivel/speedtest-cli` | network | Python |
| 460 | gping | `orf/gping` | network | Rust |
| 461 | trippy | `fujiapple852/trippy` | network | Rust |
| 462 | rustscan | `RustScan/RustScan` | security | Rust |
| 463 | gobuster | `OJ/gobuster` | security | Go |
| 464 | feroxbuster | `epi052/feroxbuster` | security | Rust |
| 465 | nikto | `sullo/nikto` | security | Perl |
| 466 | sqlmap | `sqlmapproject/sqlmap` | security | Python |
| 467 | amass | `owasp-amass/amass` | security | Go |
| 468 | unison | `bcpierce00/unison` | file-management | OCaml |
| 469 | lsyncd | `lsyncd/lsyncd` | file-management | Lua |
| 470 | duplicity | `duplicity/duplicity` | file-management | Python |
| 471 | kopia | `kopia/kopia` | file-management | Go |
| 472 | btrbk | `digint/btrbk` | file-management | Perl |
| 473 | puppet | `puppetlabs/puppet` | devops | Ruby |
| 474 | chef | `chef/chef` | devops | Ruby |
| 475 | salt | `saltstack/salt` | devops | Python |
| 476 | jenkins-cli | `jenkinsci/jenkins` | devops | Java |
| 477 | gitlab-runner | `gitlabhq/gitlab-runner` | devops | Go |
| 478 | drone-cli | `harness/drone-cli` | devops | Go |
| 479 | woodpecker-cli | `woodpecker-ci/woodpecker` | devops | Go |
| 480 | tekton-cli | `tektoncd/cli` | devops | Go |
| 481 | buildkite-agent | `buildkite/agent` | devops | Go |
| 482 | mkdocs | `mkdocs/mkdocs` | misc | Python |
| 483 | zola | `getzola/zola` | misc | Rust |
| 484 | jekyll | `jekyll/jekyll` | misc | Ruby |
| 485 | pelican | `getpelican/pelican` | misc | Python |
| 486 | eleventy | `11ty/eleventy` | misc | JavaScript |
| 487 | mdbook | `rust-lang/mdBook` | misc | Rust |
| 488 | asciidoctor | `asciidoctor/asciidoctor` | misc | Ruby |
| 489 | tldr | `tldr-pages/tldr` | misc | Markdown |
| 490 | cheat | `cheat/cheat` | misc | Go |
| 491 | navi | `denisidoro/navi` | misc | Rust |
| 492 | composer | `composer/composer` | package-manager | PHP |
| 493 | gem | `rubygems/rubygems` | package-manager | Ruby |
| 494 | bundler | `rubygems/rubygems` | package-manager | Ruby |
| 495 | mix | `elixir-lang/elixir` | package-manager | Elixir |
| 496 | pub | `dart-lang/pub` | package-manager | Dart |
| 497 | nuget | `NuGet/Home` | package-manager | C# |
| 498 | vcpkg | `microsoft/vcpkg` | package-manager | C++ |
| 499 | conan | `conan-io/conan` | package-manager | Python |
| 500 | spack | `spack/spack` | package-manager | Python |
| 501 | conda | `conda/conda` | package-manager | Python |
| 502 | mamba | `mamba-org/mamba` | package-manager | C++ |
| 503 | micromamba | `mamba-org/mamba` | package-manager | C++ |
| 504 | pixi | `prefix-dev/pixi` | package-manager | Rust |
| 505 | cqlsh | `apache/cassandra` | database | Python |
| 506 | cockroach | `cockroachdb/cockroach` | database | Go |
| 507 | vitess-vtctl | `vitessio/vitess` | database | Go |
| 508 | arangosh | `arangodb/arangodb` | database | C++ |
| 509 | cypher-shell | `neo4j/neo4j` | database | Java |
| 510 | surrealdb-cli | `surrealdb/surrealdb` | database | Rust |
| 511 | influxdb-cli | `influxdata/influx-cli` | database | Go |
| 512 | finch | `runfinch/finch` | container | Go |
| 513 | colima | `abiosoft/colima` | container | Go |
| 514 | lima | `lima-vm/lima` | container | Go |
| 515 | huggingface-cli | `huggingface/huggingface_hub` | misc | Python |
| 516 | ollama | `ollama/ollama` | misc | Go |
| 517 | llama-cpp | `ggerganov/llama.cpp` | misc | C++ |
| 518 | whisper-cpp | `ggerganov/whisper.cpp` | misc | C++ |
| 519 | figlet | `cmatsuoka/figlet` | misc | C |
| 520 | cowsay | `piuccio/cowsay` | misc | JavaScript |
| 521 | lolcat | `busyloop/lolcat` | misc | Ruby |
| 522 | cmatrix | `abishekvashok/cmatrix` | misc | C |
| 523 | fastfetch | `fastfetch-cli/fastfetch` | system | C |
| 524 | macchina | `Macchina-CLI/macchina` | system | Rust |
| 525 | pfetch | `dylanaraps/pfetch` | system | Shell |
| 526 | gifski | `ImageOptim/gifski` | media | Rust |
| 527 | gifsicle | `kohler/gifsicle` | media | C |
| 528 | termtosvg | `nbedos/termtosvg` | misc | Python |
| 529 | carbon-now-cli | `mixn/carbon-now-cli` | misc | JavaScript |
| 530 | strace | `strace/strace` | system | C |
| 531 | ltrace | `dkogan/ltrace` | system | C |
| 532 | perf | `torvalds/linux` | system | C |
| 533 | valgrind | `valgrind/valgrind` | testing | C |
| 534 | gdb | `bminor/binutils-gdb` | system | C |
| 535 | lldb | `llvm/llvm-project` | system | C++ |
| 536 | pv | `a-j-wood/pv` | misc | C |
| 537 | progress | `Xfennec/progress` | misc | C |
| 538 | parallel | `gnu-mirror/parallel` | shell | Perl |
| 539 | xargs | `coreutils/coreutils` | shell | C |
| 540 | expect | `aeruder/expect` | shell | Tcl |
| 541 | miller | `johnkerl/miller` | search | Go |
| 542 | dasel | `TomWright/dasel` | search | Go |
| 543 | fx | `antonmedv/fx` | search | Go |
| 544 | jless | `PaulJuliworker/jless` | search | Rust |
| 545 | csvkit | `wireservice/csvkit` | search | Python |
| 546 | xsv | `BurntSushi/xsv` | search | Rust |
| 547 | qsv | `jqnatividad/qsv` | search | Rust |
| 548 | pup | `ericchiang/pup` | search | Go |
| 549 | htmlq | `mgdm/htmlq` | search | Rust |
| 550 | jc | `kellyjonbrazil/jc` | search | Python |
| 551 | gron | `tomnomnom/gron` | search | Go |
| 552 | grpcui | `fullstorydev/grpcui` | network | Go |
| 553 | evans | `ktr0731/evans` | network | Go |
| 554 | websocat | `vi/websocat` | network | Rust |
| 555 | tcpflow | `simsong/tcpflow` | network | C++ |
| 556 | mitmproxy | `mitmproxy/mitmproxy` | network | Python |
| 557 | charles | `nickvdp/charles-hacking` | network | Java |
| 558 | brook | `txthinking/brook` | network | Go |
| 559 | miniserve | `svenstaro/miniserve` | network | Rust |
| 560 | pget | `Code-Hex/pget` | network | Go |
| 561 | curlie | `rs/curlie` | network | Go |
| 562 | rage | `str4d/rage` | security | Rust |
| 563 | signify | `aperezdc/signify` | security | C |
| 564 | rkhunter | `installation/rkhunter` | security | Shell |
| 565 | binwalk | `ReFirmLabs/binwalk` | security | Python |
| 566 | radare2 | `radareorg/radare2` | security | C |
| 567 | ghidra | `NationalSecurityAgency/ghidra` | security | Java |
| 568 | sentinel | `hashicorp/sentinel-sdk` | devops | Go |
| 569 | task-spooler | `justanhduc/task-spooler` | system | C |
| 570 | at | `coreutils/coreutils` | system | C |
| 571 | cron | `cronie-crond/cronie` | system | C |
| 572 | anacron | `cronie-crond/cronie` | system | C |
| 573 | logrotate | `logrotate/logrotate` | system | C |
| 574 | ccache | `ccache/ccache` | build-tool | C++ |
| 575 | sccache | `mozilla/sccache` | build-tool | Rust |
| 576 | platformio | `platformio/platformio-core` | build-tool | Python |
| 577 | esptool | `espressif/esptool` | system | Python |
| 578 | openocd | `openocd-org/openocd` | system | C |
| 579 | avrdude | `avrdudes/avrdude` | system | C |
| 580 | probe-rs | `probe-rs/probe-rs` | system | Rust |
| 581 | cargo-embed | `probe-rs/cargo-embed` | build-tool | Rust |
| 582 | cargo-flash | `probe-rs/cargo-flash` | build-tool | Rust |
| 583 | uf2conv | `microsoft/uf2` | system | Python |
| 584 | stlink | `stlink-org/stlink` | system | C |
| 585 | defmt | `knurling-rs/defmt` | system | Rust |
| 586 | lshw | `lyonel/lshw` | system | C++ |
| 587 | lspci | `pciutils/pciutils` | system | C |
| 588 | lsusb | `gregkh/usbutils` | system | C |
| 589 | dmidecode | `mirror/dmidecode` | system | C |
| 590 | smartctl | `smartmontools/smartmontools` | system | C++ |
| 591 | hdparm | `mirror/hdparm` | system | C |
| 592 | nvme-cli | `linux-nvme/nvme-cli` | system | C |
| 593 | fio | `axboe/fio` | testing | C |
| 594 | stress-ng | `ColinIanKing/stress-ng` | testing | C |
| 595 | sysbench | `akopytov/sysbench` | testing | C |
| 596 | memtester | `jnavila/memtester` | testing | C |
| 597 | gnuplot | `gnuplot/gnuplot` | media | C |
| 598 | octave | `gnu-octave/octave` | misc | C++ |
| 599 | maxima | `jvilk/maxima-mirror` | misc | Common Lisp |
| 600 | julia | `JuliaLang/julia` | misc | Julia |
| 601 | geth | `ethereum/go-ethereum` | misc | Go |
| 602 | solc | `ethereum/solidity` | build-tool | C++ |
| 603 | forge | `foundry-rs/foundry` | build-tool | Rust |
| 604 | cast | `foundry-rs/foundry` | misc | Rust |
| 605 | anvil | `foundry-rs/foundry` | testing | Rust |
| 606 | anchor | `coral-xyz/anchor` | build-tool | Rust |
| 607 | solana-cli | `solana-labs/solana` | misc | Rust |
| 608 | sox | `chirlu/sox` | media | C |
| 609 | lame | `lameproject/lame` | media | C |
| 610 | opus-tools | `xiph/opus-tools` | media | C |
| 611 | flac | `xiph/flac` | media | C |
| 612 | mpv | `mpv-player/mpv` | media | C |
| 613 | mpc | `MusicPlayerDaemon/mpc` | media | C |
| 614 | ncmpcpp | `ncmpcpp/ncmpcpp` | media | C++ |
| 615 | cmus | `cmus/cmus` | media | C |
| 616 | handbrake-cli | `HandBrake/HandBrake` | media | C |
| 617 | mkvtoolnix | `nmaier/mkvtoolnix` | media | C++ |
| 618 | x264 | `mirror/x264` | media | C |
| 619 | x265 | `multicoreware/x265_git` | media | C++ |
| 620 | aomenc | `aspect-build/aom` | media | C |
| 621 | svt-av1 | `AOMediaCodec/SVT-AV1` | media | C |
| 622 | rav1e | `xiph/rav1e` | media | Rust |
| 623 | fonttools | `fonttools/fonttools` | media | Python |
| 624 | woff2 | `google/woff2` | media | C++ |
| 625 | openscad | `openscad/openscad` | media | C++ |
| 626 | blender-cli | `blender/blender` | media | C++ |
| 627 | ghostscript | `ArtifexSoftware/ghostpdl` | media | C |
| 628 | qpdf | `qpdf/qpdf` | media | C++ |
| 629 | pdftk | `pdftk-java/pdftk` | media | Java |
| 630 | pdftotext | `freedesktop/poppler` | media | C++ |
| 631 | mutt | `muttmua/mutt` | misc | C |
| 632 | neomutt | `neomutt/neomutt` | misc | C |
| 633 | aerc | `rstrm/aerc` | misc | Go |
| 634 | himalaya | `sostrovsky/himalaya` | misc | Rust |
| 635 | notmuch | `notmuchmail/notmuch` | misc | C |
| 636 | weechat | `weechat/weechat` | misc | C |
| 637 | irssi | `irssi/irssi` | misc | C |
| 638 | profanity | `profanity-im/profanity` | misc | C |
| 639 | gomuks | `tulir/gomuks` | misc | Go |
| 640 | newsboat | `newsboat/newsboat` | misc | Rust |
| 641 | khal | `pimutils/khal` | misc | Python |
| 642 | nb | `xwmx/nb` | misc | Shell |
| 643 | joplin-cli | `laurent22/joplin` | misc | TypeScript |
| 644 | dnote | `dnote/dnote` | misc | Go |
| 645 | taskwarrior | `GothenburgBitFactory/taskwarrior` | misc | C++ |
| 646 | timewarrior | `GothenburgBitFactory/timewarrior` | misc | C++ |
| 647 | watson | `TailorDev/Watson` | misc | Python |
| 648 | 1password-cli | `1Password/connect` | security | Go |
| 649 | keepassxc-cli | `keepassxreboot/keepassxc` | security | C++ |
| 650 | doppler | `DopplerHQ/cli` | security | Go |
| 651 | teller | `tellerops/teller` | security | Go |
| 652 | openvpn | `OpenVPN/openvpn` | network | C |
| 653 | strongswan | `strongswan/strongswan` | network | C |
| 654 | wireguard-tools | `WireGuard/wireguard-tools` | network | C |
| 655 | unbound | `NLnetLabs/unbound` | network | C |
| 656 | knot-resolver | `CZ-NIC/knot-resolver` | network | C |
| 657 | squid | `squid-cache/squid` | network | C++ |
| 658 | privoxy | `fabiankeil/privoxy` | network | C |
| 659 | linkerd | `linkerd/linkerd2` | devops | Go |
| 660 | telegraf | `influxdata/telegraf` | monitoring | Go |
| 661 | collectd | `collectd/collectd` | monitoring | C |
| 662 | datadog-agent | `DataDog/datadog-agent` | monitoring | Go |
| 663 | newrelic-cli | `newrelic/newrelic-cli` | monitoring | Go |
| 664 | rsyslog | `rsyslog/rsyslog` | system | C |
| 665 | syslog-ng | `syslog-ng/syslog-ng` | system | C |
| 666 | fluentd | `fluent/fluentd` | monitoring | Ruby |
| 667 | fluent-bit | `fluent/fluent-bit` | monitoring | C |
| 668 | rdiff-backup | `rdiff-backup/rdiff-backup` | file-management | Python |
| 669 | dar | `Edrusb/DAR` | file-management | C++ |
| 670 | qemu | `qemu/qemu` | system | C |
| 671 | virsh | `libvirt/libvirt` | system | C |
| 672 | vboxmanage | `nicknisi/virtualbox` | system | C++ |
| 673 | multipass | `canonical/multipass` | system | C++ |
| 674 | firecracker | `firecracker-microvm/firecracker` | system | Rust |
| 675 | cloud-hypervisor | `cloud-hypervisor/cloud-hypervisor` | system | Rust |
| 676 | kata-runtime | `kata-containers/kata-containers` | container | Go |
| 677 | gocryptfs | `rfjakob/gocryptfs` | security | Go |
| 678 | fscrypt | `google/fscrypt` | security | Go |
| 679 | squashfs-tools | `plougher/squashfs-tools` | file-management | C |
| 680 | cargo-watch | `watchexec/cargo-watch` | build-tool | Rust |
| 681 | cargo-expand | `dtolnay/cargo-expand` | build-tool | Rust |
| 682 | cargo-clippy | `rust-lang/rust-clippy` | linter | Rust |
| 683 | cargo-audit | `rustsec/rustsec` | security | Rust |
| 684 | cargo-deny | `EmbarkStudios/cargo-deny` | security | Rust |
| 685 | cargo-nextest | `nextest-rs/nextest` | testing | Rust |
| 686 | cargo-tarpaulin | `xd009642/tarpaulin` | testing | Rust |
| 687 | miri | `rust-lang/miri` | testing | Rust |
| 688 | cppcheck | `danmar/cppcheck` | linter | C++ |
| 689 | clang-tidy | `llvm/llvm-project` | linter | C++ |
| 690 | clang-format | `llvm/llvm-project` | formatter | C++ |
| 691 | include-what-you-use | `include-what-you-use/include-what-you-use` | linter | C++ |
| 692 | bpftrace | `bpftrace/bpftrace` | monitoring | C++ |
| 693 | bcc | `iovisor/bcc` | monitoring | C++ |
| 694 | sysdig | `draios/sysdig` | monitoring | C++ |
| 695 | jo | `jpmens/jo` | misc | C |
| 696 | q | `harelba/q` | database | Python |
| 697 | trdsql | `noborus/trdsql` | database | Go |
| 698 | sqlite-utils | `simonw/sqlite-utils` | database | Python |
| 699 | datasette | `simonw/datasette` | database | Python |
| 700 | s3cmd | `s3tools/s3cmd` | cloud | Python |
| 701 | s5cmd | `peak/s5cmd` | cloud | Go |
| 702 | cue | `cue-lang/cue` | misc | Go |
| 703 | jsonnet | `google/jsonnet` | misc | C++ |
| 704 | dhall | `dhall-lang/dhall-haskell` | misc | Haskell |
| 705 | conftest | `open-policy-agent/conftest` | testing | Go |
| 706 | kubeval | `instrumenta/kubeval` | linter | Go |
| 707 | kubeconform | `yannh/kubeconform` | linter | Go |
| 708 | pluto | `FairwindsOps/pluto` | devops | Go |
| 709 | helmfile | `helmfile/helmfile` | devops | Go |
| 710 | kops | `kubernetes/kops` | devops | Go |
| 711 | calico | `projectcalico/calico` | network | Go |
| 712 | crictl | `kubernetes-sigs/cri-tools` | container | Go |
| 713 | ctr | `containerd/containerd` | container | Go |
| 714 | runc | `opencontainers/runc` | container | Go |
| 715 | crun | `containers/crun` | container | C |
| 716 | youki | `containers/youki` | container | Rust |
| 717 | kompose | `kubernetes/kompose` | devops | Go |
| 718 | ghz | `bojand/ghz` | testing | Go |
| 719 | dnscontrol | `StackExchange/dnscontrol` | network | Go |
| 720 | opentofu | `opentofu/opentofu` | devops | Go |
| 721 | yamlfmt | `google/yamlfmt` | formatter | Go |
| 722 | codespell | `codespell-project/codespell` | linter | Python |
| 723 | editorconfig-checker | `editorconfig-checker/editorconfig-checker` | linter | Go |
| 724 | oxipng | `shssoichern/oxipng` | media | Rust |
| 725 | resvg | `RazrFalcon/resvg` | media | Rust |
| 726 | dufs | `sigoden/dufs` | network | Rust |
| 727 | drill | `fcsonline/drill` | testing | Rust |
| 728 | hurl | `Orange-OpenSource/hurl` | testing | Rust |
| 729 | csvlens | `YS-L/csvlens` | file-management | Rust |
| 730 | visidata | `saulpw/visidata` | file-management | Python |
| 731 | termshark | `gcla/termshark` | network | Go |
| 732 | sniffnet | `GyulyVGC/sniffnet` | network | Rust |
| 733 | zenith | `bvaisvil/zenith` | monitoring | Rust |
| 734 | ytop | `cjbassi/ytop` | monitoring | Rust |
| 735 | gotop | `xxxserxxx/gotop` | monitoring | Go |
| 736 | bpytop | `aristocratos/bpytop` | monitoring | Python |
| 737 | werf | `werf/werf` | devops | Go |
| 738 | gefyra | `gefyrahq/gefyra` | devops | Python |
| 739 | air | `cosmtrek/air` | build-tool | Go |
| 740 | gore | `x-motemen/gore` | shell | Go |
| 741 | delve | `go-delve/delve` | testing | Go |
| 742 | gofumpt | `mvdan/gofumpt` | formatter | Go |
| 743 | golines | `segmentio/golines` | formatter | Go |
| 744 | goimports | `golang/tools` | formatter | Go |
| 745 | govulncheck | `golang/vuln` | security | Go |
| 746 | gotests | `cweill/gotests` | testing | Go |
| 747 | gotestsum | `gotestyourself/gotestsum` | testing | Go |
| 748 | goose | `pressly/goose` | database | Go |
| 749 | migrate | `golang-migrate/migrate` | database | Go |
| 750 | dbmate | `amacneil/dbmate` | database | Go |
| 751 | atlas | `ariga/atlas` | database | Go |
| 752 | sqlc | `sqlc-dev/sqlc` | database | Go |
| 753 | nfpm | `goreleaser/nfpm` | build-tool | Go |
| 754 | fpm | `jordansissel/fpm` | build-tool | Ruby |
| 755 | rubocop | `rubocop/rubocop` | linter | Ruby |
| 756 | sorbet | `sorbet/sorbet` | linter | C++ |
| 757 | solargraph | `castwide/solargraph` | linter | Ruby |
| 758 | pry | `pry/pry` | shell | Ruby |
| 759 | thor | `rails/thor` | build-tool | Ruby |
| 760 | rake | `ruby/rake` | build-tool | Ruby |
| 761 | phpstan | `phpstan/phpstan` | linter | PHP |
| 762 | psalm | `vimeo/psalm` | linter | PHP |
| 763 | phpcs | `squizlabs/PHP_CodeSniffer` | linter | PHP |
| 764 | pint | `laravel/pint` | formatter | PHP |
| 765 | pest | `pestphp/pest` | testing | PHP |
| 766 | rector | `rectorphp/rector` | build-tool | PHP |
| 767 | wp-cli | `wp-cli/wp-cli` | misc | PHP |
| 768 | symfony-cli | `symfony-cli/symfony-cli` | build-tool | Go |
| 769 | helm-diff | `databus23/helm-diff` | devops | Go |
| 770 | sealed-secrets | `bitnami-labs/sealed-secrets` | security | Go |
| 771 | external-secrets | `external-secrets/external-secrets` | security | Go |
| 772 | keda | `kedacore/keda` | devops | Go |
| 773 | knative-cli | `knative/client` | devops | Go |
| 774 | karpenter | `aws/karpenter` | cloud | Go |
| 775 | rancher-cli | `rancher/cli` | container | Go |
| 776 | mimir | `grafana/mimir` | monitoring | Go |
| 777 | pyroscope | `grafana/pyroscope` | monitoring | Go |
| 778 | alloy | `grafana/alloy` | monitoring | Go |
| 779 | promtool | `prometheus/prometheus` | monitoring | Go |
| 780 | amtool | `prometheus/alertmanager` | monitoring | Go |
| 781 | kubecost | `kubecost/cost-analyzer-helm-chart` | monitoring | Go |
| 782 | opencost | `opencost/opencost` | monitoring | Go |
| 783 | leapp | `Noovolari/leapp` | cloud | TypeScript |
| 784 | ali | `nakabonne/ali` | testing | Go |
| 785 | toxiproxy | `Shopify/toxiproxy` | testing | Go |
| 786 | chaos-mesh | `chaos-mesh/chaos-mesh` | testing | Go |
| 787 | litmus | `litmuschaos/litmus` | testing | Go |
| 788 | pumba | `alexei-led/pumba` | testing | Go |
| 789 | metallb | `metallb/metallb` | network | Go |
| 790 | contour | `projectcontour/contour` | network | Go |
| 791 | hubble | `cilium/hubble` | network | Go |
| 792 | cdk | `aws/aws-cdk` | cloud | TypeScript |
| 793 | amplify-cli | `aws-amplify/amplify-cli` | cloud | TypeScript |
| 794 | edgedb-cli | `edgedb/edgedb-cli` | database | Rust |
| 795 | fauna-cli | `fauna/fauna-shell` | database | JavaScript |
| 796 | convex-cli | `get-convex/convex-backend` | database | TypeScript |
| 797 | upstash-cli | `upstash/cli` | database | Go |
| 798 | tv | `alexhallam/tv` | file-management | Rust |
| 799 | vivid | `sharkdp/vivid` | shell | Rust |
| 800 | pastel | `sharkdp/pastel` | misc | Rust |
| 801 | hexyl | `sharkdp/hexyl` | file-management | Rust |
| 802 | binocle | `sharkdp/binocle` | file-management | Rust |
| 803 | tealdeer | `dbrgn/tealdeer` | misc | Rust |
| 804 | trunk | `thedodd/trunk` | build-tool | Rust |
| 805 | wasm-pack | `rustwasm/wasm-pack` | build-tool | Rust |
| 806 | cargo-flamegraph | `flamegraph-rs/flamegraph` | monitoring | Rust |
| 807 | cargo-bloat | `RazrFalcon/cargo-bloat` | build-tool | Rust |
| 808 | gitoxide | `Byron/gitoxide` | version-control | Rust |
| 809 | jujutsu | `martinvonz/jj` | version-control | Rust |
| 810 | sapling | `facebook/sapling` | version-control | Rust |
| 811 | pijul | `pijul-scm/pijul` | version-control | Rust |
| 812 | watchman | `facebook/watchman` | file-management | C++ |
| 813 | dstat | `dagwieers/dstat` | monitoring | Python |
| 814 | iotop | `Tomas-M/iotop` | monitoring | C |
| 815 | sealer | `sealerio/sealer` | container | Go |
| 816 | sealos | `labring/sealos` | container | Go |
| 817 | kail | `boz/kail` | monitoring | Go |
| 818 | kubetail | `johanhaleby/kubetail` | monitoring | Shell |
| 819 | nova | `FairwindsOps/nova` | linter | Go |
| 820 | kubeadm | `kubernetes/kubernetes` | devops | Go |
| 821 | clusterctl | `kubernetes-sigs/cluster-api` | devops | Go |
| 822 | talosctl | `siderolabs/talos` | devops | Go |
| 823 | pkl | `apple/pkl` | build-tool | Kotlin |
| 824 | ytt | `carvel-dev/ytt` | build-tool | Go |
| 825 | kapp | `carvel-dev/kapp` | devops | Go |
| 826 | imgpkg | `carvel-dev/imgpkg` | container | Go |
| 827 | vendir | `carvel-dev/vendir` | package-manager | Go |
| 828 | regctl | `regclient/regclient` | container | Go |
| 829 | dockle | `goodwithtech/dockle` | security | Go |
| 830 | slim | `slimtoolkit/slim` | container | Go |
| 831 | ttyd | `tsl0922/ttyd` | shell | C |
| 832 | upterm | `owenthereal/upterm` | shell | Go |
| 833 | sshx | `ekzhang/sshx` | shell | Rust |
| 834 | vals | `helmfile/vals` | security | Go |
| 835 | transcrypt | `elasticdog/transcrypt` | security | Shell |
| 836 | jsonlint | `zaach/jsonlint` | linter | JavaScript |
| 837 | commitlint | `conventional-changelog/commitlint` | linter | JavaScript |
| 838 | less | `gnu-mirror/less` | file-management | C |
| 839 | more | `util-linux/util-linux` | file-management | C |
| 840 | cat | `coreutils/coreutils` | file-management | C |
| 841 | head | `coreutils/coreutils` | file-management | C |
| 842 | tail | `coreutils/coreutils` | file-management | C |
| 843 | diff | `gnu-mirror/diffutils` | file-management | C |
| 844 | patch | `gnu-mirror/patch` | file-management | C |
| 845 | file | `file/file` | file-management | C |
| 846 | stat | `coreutils/coreutils` | file-management | C |
| 847 | dd | `coreutils/coreutils` | file-management | C |
| 848 | cp | `coreutils/coreutils` | file-management | C |
| 849 | mv | `coreutils/coreutils` | file-management | C |
| 850 | rm | `coreutils/coreutils` | file-management | C |
| 851 | mkdir | `coreutils/coreutils` | file-management | C |
| 852 | chmod | `coreutils/coreutils` | file-management | C |
| 853 | chown | `coreutils/coreutils` | file-management | C |
| 854 | ln | `coreutils/coreutils` | file-management | C |
| 855 | ls | `coreutils/coreutils` | file-management | C |
| 856 | touch | `coreutils/coreutils` | file-management | C |
| 857 | mktemp | `coreutils/coreutils` | file-management | C |
| 858 | find | `gnu-mirror/findutils` | search | C |
| 859 | locate | `gnu-mirror/findutils` | search | C |
| 860 | grep | `gnu-mirror/grep` | search | C |
| 861 | bfs | `tavianator/bfs` | search | C |
| 862 | ugrep | `Genivia/ugrep` | search | C++ |
| 863 | ast-grep | `ast-grep/ast-grep` | search | Rust |
| 864 | amber | `dalance/amber` | search | Rust |
| 865 | angle-grinder | `rcoh/angle-grinder` | search | Rust |
| 866 | jnv | `ynqa/jnv` | search | Rust |
| 867 | which | `gnu-mirror/which` | shell | C |
| 868 | env | `coreutils/coreutils` | shell | C |
| 869 | test | `coreutils/coreutils` | shell | C |
| 870 | bash | `bminor/bash` | shell | C |
| 871 | dash | `pbs/dash` | shell | C |
| 872 | pwsh | `PowerShell/PowerShell` | shell | C# |
| 873 | elvish | `elves/elvish` | shell | Go |
| 874 | xonsh | `xonsh/xonsh` | shell | Python |
| 875 | oil | `oilshell/oil` | shell | Python |
| 876 | murex | `lmorg/murex` | shell | Go |
| 877 | oh-my-posh | `JanDeDobbeleer/oh-my-posh` | shell | Go |
| 878 | carapace | `carapace-sh/carapace-bin` | shell | Go |
| 879 | mcfly | `cantino/mcfly` | shell | Rust |
| 880 | hstr | `dvorka/hstr` | shell | C |
| 881 | watch | `procps-ng/procps` | system | C |
| 882 | timeout | `coreutils/coreutils` | system | C |
| 883 | nice | `coreutils/coreutils` | system | C |
| 884 | dmesg | `util-linux/util-linux` | system | C |
| 885 | journalctl | `systemd/systemd` | system | C |
| 886 | timedatectl | `systemd/systemd` | system | C |
| 887 | hostnamectl | `systemd/systemd` | system | C |
| 888 | loginctl | `systemd/systemd` | system | C |
| 889 | sysctl | `procps-ng/procps` | system | C |
| 890 | modprobe | `kmod-project/kmod` | system | C |
| 891 | lsmod | `kmod-project/kmod` | system | C |
| 892 | udevadm | `systemd/systemd` | system | C |
| 893 | blkid | `util-linux/util-linux` | system | C |
| 894 | lsblk | `util-linux/util-linux` | system | C |
| 895 | mount | `util-linux/util-linux` | system | C |
| 896 | findmnt | `util-linux/util-linux` | system | C |
| 897 | df | `coreutils/coreutils` | system | C |
| 898 | free | `procps-ng/procps` | system | C |
| 899 | uptime | `procps-ng/procps` | system | C |
| 900 | who | `coreutils/coreutils` | system | C |
| 901 | id | `coreutils/coreutils` | system | C |
| 902 | useradd | `shadow-maint/shadow` | system | C |
| 903 | passwd | `shadow-maint/shadow` | system | C |
| 904 | sudo | `sudo-project/sudo` | system | C |
| 905 | doas | `Duncaen/OpenDoas` | system | C |
| 906 | kill | `procps-ng/procps` | system | C |
| 907 | pkill | `procps-ng/procps` | system | C |
| 908 | nohup | `coreutils/coreutils` | system | C |
| 909 | crontab | `cronie-crond/cronie` | system | C |
| 910 | date | `coreutils/coreutils` | system | C |
| 911 | sleep | `coreutils/coreutils` | system | C |
| 912 | du | `coreutils/coreutils` | system | C |
| 913 | ps | `procps-ng/procps` | system | C |
| 914 | xsel | `kfish/xsel` | system | C |
| 915 | xclip | `astrand/xclip` | system | C |
| 916 | wl-clipboard | `bugaevc/wl-clipboard` | system | C |
| 917 | rofi | `davatorium/rofi` | system | C |
| 918 | ip | `iproute2/iproute2` | network | C |
| 919 | ss | `iproute2/iproute2` | network | C |
| 920 | hostname | `util-linux/util-linux` | network | C |
| 921 | tc | `iproute2/iproute2` | network | C |
| 922 | ethtool | `netoptimizer/ethtool` | network | C |
| 923 | nmcli | `NetworkManager/NetworkManager` | network | C |
| 924 | dig | `isc-projects/bind9` | network | C |
| 925 | ping | `iputils/iputils` | network | C |
| 926 | traceroute | `openbsd/src` | network | C |
| 927 | netcat | `openbsd/src` | network | C |
| 928 | whois | `rfc1036/whois` | network | C |
| 929 | ssh | `openssh/openssh-portable` | network | C |
| 930 | scp | `openssh/openssh-portable` | network | C |
| 931 | sftp | `openssh/openssh-portable` | network | C |
| 932 | doggo | `mr-karan/doggo` | network | Go |
| 933 | vultr-cli | `vultr/vultr-cli` | cloud | Go |
| 934 | scaleway-cli | `scaleway/scaleway-cli` | cloud | Go |
| 935 | flarectl | `cloudflare/cloudflare-go` | cloud | Go |
| 936 | railway-cli | `railwayapp/cli` | cloud | Rust |
| 937 | render-cli | `render-oss/render-cli` | cloud | Go |
| 938 | oci-cli | `oracle/oci-cli` | cloud | Python |
| 939 | upcloud-cli | `UpCloudLtd/upcloud-cli` | cloud | Go |
| 940 | pg_dump | `postgres/postgres` | database | C |
| 941 | pg_restore | `postgres/postgres` | database | C |
| 942 | pgbench | `postgres/postgres` | database | C |
| 943 | percona-toolkit | `percona/percona-toolkit` | database | Perl |
| 944 | gh-ost | `github/gh-ost` | database | Go |
| 945 | tiup | `pingcap/tiup` | database | Go |
| 946 | valkey-cli | `valkey-io/valkey` | database | C |
| 947 | dragonfly | `dragonflydb/dragonfly` | database | C++ |
| 948 | keydb-cli | `Snapchat/KeyDB` | database | C++ |
| 949 | foundationdb-cli | `apple/foundationdb` | database | C++ |
| 950 | yugabyte-cli | `yugabyte/yugabyte-db` | database | Java |
| 951 | pgloader | `dimitri/pgloader` | database | Common Lisp |
| 952 | mydumper | `mydumper/mydumper` | database | C |
| 953 | sqlboiler | `volatiletech/sqlboiler` | database | Go |
| 954 | bacon | `Canop/bacon` | build-tool | Rust |
| 955 | cargo-outdated | `kbknapp/cargo-outdated` | package-manager | Rust |
| 956 | cargo-edit | `killercup/cargo-edit` | package-manager | Rust |
| 957 | cargo-generate | `cargo-generate/cargo-generate` | build-tool | Rust |
| 958 | cargo-release | `crate-ci/cargo-release` | build-tool | Rust |
| 959 | cargo-make | `sagiegurari/cargo-make` | build-tool | Rust |
| 960 | cross | `cross-rs/cross` | build-tool | Rust |
| 961 | leptosfmt | `bram209/leptosfmt` | formatter | Rust |
| 962 | dioxus-cli | `DioxusLabs/dioxus` | build-tool | Rust |
| 963 | mdbook-mermaid | `badboy/mdbook-mermaid` | misc | Rust |
| 964 | ouch | `ouch-org/ouch` | file-management | Rust |
| 965 | silicon | `Aloxaf/silicon` | misc | Rust |
| 966 | tokio-console | `tokio-rs/console` | monitoring | Rust |
| 967 | cobra-cli | `spf13/cobra-cli` | build-tool | Go |
| 968 | templ | `a-h/templ` | build-tool | Go |
| 969 | gqlgen | `99designs/gqlgen` | build-tool | Go |
| 970 | ent | `ent/ent` | build-tool | Go |
| 971 | swag | `swaggo/swag` | build-tool | Go |
| 972 | oapi-codegen | `deepmap/oapi-codegen` | build-tool | Go |
| 973 | mockgen | `uber-go/mock` | testing | Go |
| 974 | wire | `google/wire` | build-tool | Go |
| 975 | npx | `npm/npx` | package-manager | JavaScript |
| 976 | corepack | `nodejs/corepack` | package-manager | TypeScript |
| 977 | volta | `volta-cli/volta` | package-manager | Rust |
| 978 | fnm | `Schniz/fnm` | package-manager | Rust |
| 979 | n | `tj/n` | package-manager | Shell |
| 980 | ni | `antfu/ni` | package-manager | TypeScript |
| 981 | taze | `antfu/taze` | package-manager | TypeScript |
| 982 | publint | `bluwy/publint` | linter | JavaScript |
| 983 | syncpack | `JamieMason/syncpack` | package-manager | TypeScript |
| 984 | top | `procps-ng/procps` | monitoring | C |
| 985 | lnav | `tstack/lnav` | monitoring | C++ |
| 986 | multitail | `folkertvanheusden/multitail` | monitoring | C |
| 987 | btop | `aristocratos/btop` | monitoring | C++ |
| 988 | nmon | `axibase/nmon` | monitoring | C |
| 989 | below | `facebookincubator/below` | monitoring | Rust |
| 990 | atop | `Atoptool/atop` | monitoring | C |
| 991 | tsung | `processone/tsung` | testing | Erlang |
| 992 | bc | `gnu-mirror/bc` | misc | C |
| 993 | seq | `coreutils/coreutils` | misc | C |
| 994 | cal | `util-linux/util-linux` | misc | C |
| 995 | yes | `coreutils/coreutils` | misc | C |
| 996 | pet | `knqyf263/pet` | misc | Go |
| 997 | chafa | `hpjansson/chafa` | media | C |
| 998 | choose-gui | `chipsenkbeil/choose` | system | Rust |
| 999 | hwatch | `blacknon/hwatch` | system | Rust |
| 1000 | prr | `danobi/prr` | version-control | Rust |

### Python Packages (1000 projects, 136 categories)

| # | Name | Repo | Category |
|---|------|------|----------|
| 1 | django | `django/django` | web-framework |
| 2 | flask | `pallets/flask` | web-framework |
| 3 | fastapi | `tiangolo/fastapi` | web-framework |
| 4 | starlette | `encode/starlette` | web-framework |
| 5 | tornado | `tornadoweb/tornado` | web-framework |
| 6 | sanic | `sanic-org/sanic` | web-framework |
| 7 | uvicorn | `encode/uvicorn` | web-framework |
| 8 | gunicorn | `benoitc/gunicorn` | web-framework |
| 9 | django-rest-framework | `encode/django-rest-framework` | api |
| 10 | graphene | `graphql-python/graphene` | api |
| 11 | grpcio | `grpc/grpc` | protocol |
| 12 | aiohttp | `aio-libs/aiohttp` | async |
| 13 | trio | `python-trio/trio` | async |
| 14 | anyio | `agronholm/anyio` | async |
| 15 | celery | `celery/celery` | task-queue |
| 16 | rq | `rq/rq` | task-queue |
| 17 | huey | `coleifer/huey` | task-queue |
| 18 | redis-py | `redis/redis-py` | database |
| 19 | pymongo | `mongodb/mongo-python-driver` | database |
| 20 | motor | `mongodb/motor` | database |
| 21 | psycopg2 | `psycopg/psycopg2` | database |
| 22 | psycopg3 | `psycopg/psycopg` | database |
| 23 | asyncpg | `MagicStack/asyncpg` | database |
| 24 | aiomysql | `aio-libs/aiomysql` | database |
| 25 | aiosqlite | `omnilib/aiosqlite` | database |
| 26 | tinydb | `msiemens/tinydb` | database |
| 27 | elasticsearch-py | `elastic/elasticsearch-py` | database |
| 28 | sqlalchemy | `sqlalchemy/sqlalchemy` | orm |
| 29 | alembic | `sqlalchemy/alembic` | orm |
| 30 | peewee | `coleifer/peewee` | orm |
| 31 | tortoise-orm | `tortoise/tortoise-orm` | orm |
| 32 | sqlmodel | `tiangolo/sqlmodel` | orm |
| 33 | pydantic | `pydantic/pydantic` | validation |
| 34 | marshmallow | `marshmallow-code/marshmallow` | serialization |
| 35 | attrs | `python-attrs/attrs` | validation |
| 36 | orjson | `ijl/orjson` | serialization |
| 37 | msgpack | `msgpack/msgpack-python` | serialization |
| 38 | protobuf | `protocolbuffers/protobuf` | serialization |
| 39 | numpy | `numpy/numpy` | scientific |
| 40 | pandas | `pandas-dev/pandas` | data-processing |
| 41 | polars | `pola-rs/polars` | data-processing |
| 42 | dask | `dask/dask` | data-processing |
| 43 | modin | `modin-project/modin` | data-processing |
| 44 | pyarrow | `apache/arrow` | data-processing |
| 45 | scipy | `scipy/scipy` | scientific |
| 46 | sympy | `sympy/sympy` | math |
| 47 | statsmodels | `statsmodels/statsmodels` | scientific |
| 48 | networkx | `networkx/networkx` | scientific |
| 49 | scikit-learn | `scikit-learn/scikit-learn` | ml |
| 50 | xgboost | `dmlc/xgboost` | ml |
| 51 | lightgbm | `microsoft/LightGBM` | ml |
| 52 | catboost | `catboost/catboost` | ml |
| 53 | optuna | `optuna/optuna` | ml |
| 54 | mlflow | `mlflow/mlflow` | ml |
| 55 | wandb | `wandb/wandb` | ml |
| 56 | ray | `ray-project/ray` | ml |
| 57 | dvc | `iterative/dvc` | ml |
| 58 | great-expectations | `great-expectations/great_expectations` | validation |
| 59 | pandera | `unionai-oss/pandera` | validation |
| 60 | pytorch | `pytorch/pytorch` | dl |
| 61 | tensorflow | `tensorflow/tensorflow` | dl |
| 62 | keras | `keras-team/keras` | dl |
| 63 | jax | `google/jax` | dl |
| 64 | flax | `google/flax` | dl |
| 65 | transformers | `huggingface/transformers` | nlp |
| 66 | datasets | `huggingface/datasets` | data-processing |
| 67 | tokenizers | `huggingface/tokenizers` | nlp |
| 68 | accelerate | `huggingface/accelerate` | dl |
| 69 | peft | `huggingface/peft` | dl |
| 70 | trl | `huggingface/trl` | dl |
| 71 | diffusers | `huggingface/diffusers` | dl |
| 72 | safetensors | `huggingface/safetensors` | dl |
| 73 | sentence-transformers | `UKPLab/sentence-transformers` | nlp |
| 74 | spacy | `explosion/spaCy` | nlp |
| 75 | nltk | `nltk/nltk` | nlp |
| 76 | gensim | `RaRe-Technologies/gensim` | nlp |
| 77 | flair | `flairNLP/flair` | nlp |
| 78 | langchain | `langchain-ai/langchain` | ml |
| 79 | llama-index | `run-llama/llama_index` | ml |
| 80 | openai | `openai/openai-python` | api |
| 81 | anthropic | `anthropics/anthropic-sdk-python` | api |
| 82 | litellm | `BerriAI/litellm` | api |
| 83 | vllm | `vllm-project/vllm` | ml |
| 84 | ollama | `ollama/ollama-python` | api |
| 85 | guidance | `guidance-ai/guidance` | ml |
| 86 | outlines | `outlines-dev/outlines` | ml |
| 87 | instructor | `jxnl/instructor` | ml |
| 88 | dspy | `stanfordnlp/dspy` | ml |
| 89 | crewai | `crewAIInc/crewAI` | ml |
| 90 | autogen | `microsoft/autogen` | ml |
| 91 | pillow | `python-pillow/Pillow` | image |
| 92 | opencv-python | `opencv/opencv-python` | cv |
| 93 | torchvision | `pytorch/vision` | cv |
| 94 | albumentations | `albumentations-team/albumentations` | cv |
| 95 | matplotlib | `matplotlib/matplotlib` | visualization |
| 96 | seaborn | `mwaskom/seaborn` | visualization |
| 97 | plotly | `plotly/plotly.py` | visualization |
| 98 | bokeh | `bokeh/bokeh` | visualization |
| 99 | altair | `altair-viz/altair` | visualization |
| 100 | streamlit | `streamlit/streamlit` | visualization |
| 101 | gradio | `gradio-app/gradio` | visualization |
| 102 | panel | `holoviz/panel` | visualization |
| 103 | dash | `plotly/dash` | visualization |
| 104 | nicegui | `zauberzeug/nicegui` | gui |
| 105 | reflex | `reflex-dev/reflex` | web-framework |
| 106 | taipy | `Avaiga/taipy` | visualization |
| 107 | requests | `psf/requests` | http-client |
| 108 | httpx | `encode/httpx` | http-client |
| 109 | urllib3 | `urllib3/urllib3` | http-client |
| 110 | beautifulsoup4 | `waylan/beautifulsoup` | scraping |
| 111 | scrapy | `scrapy/scrapy` | scraping |
| 112 | selenium | `SeleniumHQ/selenium` | scraping |
| 113 | playwright | `microsoft/playwright-python` | scraping |
| 114 | lxml | `lxml/lxml` | scraping |
| 115 | pytest | `pytest-dev/pytest` | testing |
| 116 | tox | `tox-dev/tox` | testing |
| 117 | coverage | `nedbat/coveragepy` | testing |
| 118 | hypothesis | `HypothesisWorks/hypothesis` | testing |
| 119 | faker | `joke2k/faker` | testing |
| 120 | factory-boy | `FactoryBoy/factory_boy` | testing |
| 121 | click | `pallets/click` | cli |
| 122 | typer | `tiangolo/typer` | cli |
| 123 | rich | `Textualize/rich` | tui |
| 124 | textual | `Textualize/textual` | tui |
| 125 | prompt-toolkit | `prompt-toolkit/python-prompt-toolkit` | tui |
| 126 | fire | `google/python-fire` | cli |
| 127 | prefect | `PrefectHQ/prefect` | devops |
| 128 | airflow | `apache/airflow` | devops |
| 129 | luigi | `spotify/luigi` | devops |
| 130 | dagster | `dagster-io/dagster` | devops |
| 131 | boto3 | `boto/boto3` | aws |
| 132 | google-cloud-storage | `googleapis/python-storage` | gcp |
| 133 | azure-storage-blob | `Azure/azure-sdk-for-python` | azure |
| 134 | paramiko | `paramiko/paramiko` | network |
| 135 | fabric | `fabric/fabric` | automation |
| 136 | invoke | `pyinvoke/invoke` | automation |
| 137 | ansible-core | `ansible/ansible` | devops |
| 138 | docker-py | `docker/docker-py` | devops |
| 139 | kubernetes | `kubernetes-client/python` | devops |
| 140 | pulumi | `pulumi/pulumi-python` | devops |
| 141 | loguru | `Delgan/loguru` | logging |
| 142 | structlog | `hynek/structlog` | logging |
| 143 | python-dotenv | `theskumar/python-dotenv` | config |
| 144 | dynaconf | `dynaconf/dynaconf` | config |
| 145 | hydra-core | `facebookresearch/hydra` | config |
| 146 | pyyaml | `yaml/pyyaml` | config |
| 147 | toml | `uiri/toml` | config |
| 148 | mypy | `python/mypy` | typing |
| 149 | pyright | `microsoft/pyright` | typing |
| 150 | ruff | `astral-sh/ruff` | linter |
| 151 | black | `psf/black` | formatter |
| 152 | isort | `PyCQA/isort` | formatter |
| 153 | flake8 | `PyCQA/flake8` | linter |
| 154 | pylint | `pylint-dev/pylint` | linter |
| 155 | bandit | `PyCQA/bandit` | security |
| 156 | safety | `pyupio/safety` | security |
| 157 | cryptography | `pyca/cryptography` | crypto |
| 158 | pyjwt | `jpadilla/pyjwt` | auth |
| 159 | passlib | `glic3rern/passlib` | auth |
| 160 | python-jose | `mpdavis/python-jose` | auth |
| 161 | authlib | `lepture/authlib` | auth |
| 162 | social-auth-core | `python-social-auth/social-core` | auth |
| 163 | oauthlib | `oauthlib/oauthlib` | auth |
| 164 | stripe | `stripe/stripe-python` | payment |
| 165 | twilio | `twilio/twilio-python` | sms |
| 166 | sendgrid | `sendgrid/sendgrid-python` | email |
| 167 | slack-sdk | `slackapi/python-slack-sdk` | api |
| 168 | discord-py | `Rapptz/discord.py` | api |
| 169 | python-telegram-bot | `python-telegram-bot/python-telegram-bot` | api |
| 170 | arrow | `arrow-py/arrow` | date-time |
| 171 | pendulum | `sdispater/pendulum` | date-time |
| 172 | python-dateutil | `dateutil/dateutil` | date-time |
| 173 | pytz | `stub42/pytz` | date-time |
| 174 | babel | `python-babel/babel` | text |
| 175 | jinja2 | `pallets/jinja` | template |
| 176 | mako | `sqlalchemy/mako` | template |
| 177 | sphinx | `sphinx-doc/sphinx` | documentation |
| 178 | mkdocs | `mkdocs/mkdocs` | documentation |
| 179 | h5py | `h5py/h5py` | file-processing |
| 180 | openpyxl | `theorchard/openpyxl` | excel |
| 181 | xlsxwriter | `jmcnamara/XlsxWriter` | excel |
| 182 | python-pptx | `scanny/python-pptx` | file-processing |
| 183 | python-docx | `python-openxml/python-docx` | file-processing |
| 184 | reportlab | `MrBitBucket/reportlab-mirror` | pdf |
| 185 | pypdf | `py-pdf/pypdf` | pdf |
| 186 | camelot-py | `camelot-dev/camelot` | pdf |
| 187 | pdfplumber | `jsvine/pdfplumber` | pdf |
| 188 | graphviz | `xflr6/graphviz` | visualization |
| 189 | igraph | `igraph/python-igraph` | scientific |
| 190 | sentry-sdk | `getsentry/sentry-python` | monitoring |
| 191 | prometheus-client | `prometheus/client_python` | monitoring |
| 192 | setuptools | `pypa/setuptools` | packaging |
| 193 | poetry | `python-poetry/poetry` | packaging |
| 194 | hatch | `pypa/hatch` | packaging |
| 195 | pygments | `pygments/pygments` | text |
| 196 | pexpect | `pexpect/pexpect` | automation |
| 197 | watchdog | `gorakhargosh/watchdog` | file-processing |
| 198 | tqdm | `tqdm/tqdm` | cli |
| 199 | tenacity | `jd/tenacity` | misc |
| 200 | more-itertools | `more-itertools/more-itertools` | misc |
| 201 | nox | `wntrblm/nox` | testing |
| 202 | pre-commit | `pre-commit/pre-commit` | dev-tools |
| 203 | blinker | `pallets-eco/blinker` | misc |
| 204 | wrapt | `GrahamDumpleton/wrapt` | misc |
| 205 | decorator | `micheles/decorator` | misc |
| 206 | boltons | `mahmoud/boltons` | misc |
| 207 | toolz | `pytoolz/toolz` | functional |
| 208 | cytoolz | `pytoolz/cytoolz` | functional |
| 209 | funcy | `Suor/funcy` | functional |
| 210 | returns | `dry-python/returns` | functional |
| 211 | pyrsistent | `tobgu/pyrsistent` | data-structures |
| 212 | immutables | `MagicStack/immutables` | data-structures |
| 213 | frozendict | `Marco-Sulla/python-frozendict` | data-structures |
| 214 | sortedcontainers | `grantjenks/python-sortedcontainers` | data-structures |
| 215 | intervaltree | `chaimleib/intervaltree` | data-structures |
| 216 | bitarray | `ilanschnell/bitarray` | data-structures |
| 217 | ciso8601 | `closeio/ciso8601` | date-time |
| 218 | tzdata | `python/tzdata` | date-time |
| 219 | backoff | `litl/backoff` | misc |
| 220 | stamina | `hynek/stamina` | misc |
| 221 | apscheduler | `agronholm/apscheduler` | scheduling |
| 222 | schedule | `dbader/schedule` | scheduling |
| 223 | dramatiq | `Bogdanp/dramatiq` | task-queue |
| 224 | arq | `samuelcolvin/arq` | task-queue |
| 225 | taskiq | `taskiq-python/taskiq` | task-queue |
| 226 | saq | `tobymao/saq` | task-queue |
| 227 | faststream | `airtai/faststream` | messaging |
| 228 | faust-streaming | `faust-streaming/faust` | streaming |
| 229 | confluent-kafka | `confluentinc/confluent-kafka-python` | messaging |
| 230 | pika | `pika/pika` | messaging |
| 231 | kombu | `celery/kombu` | messaging |
| 232 | aio-pika | `mosquito/aio-pika` | messaging |
| 233 | nats-py | `nats-io/nats.py` | messaging |
| 234 | pyzmq | `zeromq/pyzmq` | messaging |
| 235 | rpyc | `tomerfiliba-org/rpyc` | rpc |
| 236 | zeep | `mvantellingen/python-zeep` | protocol |
| 237 | httptools | `MagicStack/httptools` | http-client |
| 238 | websockets | `python-websockets/websockets` | protocol |
| 239 | wsproto | `python-hyper/wsproto` | protocol |
| 240 | litestar | `litestar-org/litestar` | web-framework |
| 241 | blacksheep | `Neoteroi/BlackSheep` | web-framework |
| 242 | robyn | `sansyrox/robyn` | web-framework |
| 243 | falcon | `falconry/falcon` | web-framework |
| 244 | bottle | `bottlepy/bottle` | web-framework |
| 245 | cherrypy | `cherrypy/cherrypy` | web-framework |
| 246 | pyramid | `Pylons/pyramid` | web-framework |
| 247 | connexion | `spec-first/connexion` | api |
| 248 | flask-restx | `python-restx/flask-restx` | api |
| 249 | flask-smorest | `marshmallow-code/flask-smorest` | api |
| 250 | flask-login | `maxcountryman/flask-login` | auth |
| 251 | flask-mail | `mattupstate/flask-mail` | email |
| 252 | flask-migrate | `miguelgrinberg/Flask-Migrate` | database |
| 253 | flask-sqlalchemy | `pallets-eco/flask-sqlalchemy` | orm |
| 254 | flask-caching | `pallets-eco/flask-caching` | caching |
| 255 | flask-cors | `corydolphin/flask-cors` | web-framework |
| 256 | flask-jwt-extended | `vimalloc/flask-jwt-extended` | auth |
| 257 | flask-socketio | `miguelgrinberg/Flask-SocketIO` | web-framework |
| 258 | django-allauth | `pennersr/django-allauth` | auth |
| 259 | django-cors-headers | `adamchainz/django-cors-headers` | web-framework |
| 260 | django-filter | `carltongibson/django-filter` | web-framework |
| 261 | django-celery-beat | `celery/django-celery-beat` | task-queue |
| 262 | django-debug-toolbar | `jazzband/django-debug-toolbar` | dev-tools |
| 263 | django-extensions | `django-extensions/django-extensions` | web-framework |
| 264 | django-guardian | `django-guardian/django-guardian` | auth |
| 265 | django-mptt | `django-mptt/django-mptt` | web-framework |
| 266 | django-storages | `jschneier/django-storages` | web-framework |
| 267 | django-channels | `django/channels` | web-framework |
| 268 | django-ninja | `vitalik/django-ninja` | api |
| 269 | django-environ | `joke2k/django-environ` | config |
| 270 | wagtail | `wagtail/wagtail` | cms |
| 271 | strawberry-graphql | `strawberry-graphql/strawberry` | api |
| 272 | ariadne | `mirumee/ariadne` | api |
| 273 | sgqlc | `profusion/sgqlc` | api |
| 274 | gql | `graphql-python/gql` | api |
| 275 | databases | `encode/databases` | database |
| 276 | piccolo | `piccolo-orm/piccolo` | orm |
| 277 | edgedb-python | `edgedb/edgedb-python` | database |
| 278 | cassandra-driver | `datastax/python-driver` | database |
| 279 | happybase | `python-happybase/happybase` | database |
| 280 | pymemcache | `pinterest/pymemcache` | caching |
| 281 | diskcache | `grantjenks/python-diskcache` | caching |
| 282 | cachetools | `tkem/cachetools` | caching |
| 283 | aiocache | `aio-libs/aiocache` | caching |
| 284 | filelock | `tox-dev/py-filelock` | misc |
| 285 | portalocker | `WoLpH/portalocker` | misc |
| 286 | joblib | `joblib/joblib` | parallel |
| 287 | loky | `joblib/loky` | parallel |
| 288 | dill | `uqfoundation/dill` | serialization |
| 289 | cloudpickle | `cloudpipe/cloudpickle` | serialization |
| 290 | lmdb | `jnwatson/py-lmdb` | database |
| 291 | ultrajson | `ultrajson/ultrajson` | serialization |
| 292 | simplejson | `simplejson/simplejson` | serialization |
| 293 | python-rapidjson | `python-rapidjson/python-rapidjson` | serialization |
| 294 | cbor2 | `agronholm/cbor2` | serialization |
| 295 | fastavro | `fastavro/fastavro` | serialization |
| 296 | flatbuffers | `google/flatbuffers` | serialization |
| 297 | betterproto | `danielgtaylor/python-betterproto` | serialization |
| 298 | dataclasses-json | `lidatong/dataclasses-json` | serialization |
| 299 | cattrs | `python-attrs/cattrs` | serialization |
| 300 | dacite | `konradhalas/dacite` | serialization |
| 301 | cerberus | `pyeve/cerberus` | validation |
| 302 | voluptuous | `alecthomas/voluptuous` | validation |
| 303 | jsonschema | `python-jsonschema/jsonschema` | validation |
| 304 | fastjsonschema | `horejsek/python-fastjsonschema` | validation |
| 305 | pydantic-settings | `pydantic/pydantic-settings` | config |
| 306 | python-multipart | `andrew-d/python-multipart` | http-client |
| 307 | python-magic | `ahupp/python-magic` | file-processing |
| 308 | filetype | `h2non/filetype.py` | file-processing |
| 309 | chardet | `chardet/chardet` | text |
| 310 | charset-normalizer | `Ousret/charset_normalizer` | text |
| 311 | ftfy | `rspeer/python-ftfy` | text |
| 312 | unidecode | `avian2/unidecode` | text |
| 313 | python-slugify | `un33k/python-slugify` | text |
| 314 | deep-translator | `nidhaloff/deep-translator` | nlp |
| 315 | langdetect | `Mimino666/langdetect` | nlp |
| 316 | keybert | `MaartenGr/KeyBERT` | nlp |
| 317 | bertopic | `MaartenGr/BERTopic` | nlp |
| 318 | annoy | `spotify/annoy` | ml |
| 319 | faiss | `facebookresearch/faiss` | ml |
| 320 | hnswlib | `nmslib/hnswlib` | ml |
| 321 | chromadb | `chroma-core/chroma` | database |
| 322 | weaviate-client | `weaviate/weaviate-python-client` | database |
| 323 | qdrant-client | `qdrant/qdrant-client` | database |
| 324 | pinecone-client | `pinecone-io/pinecone-python-client` | database |
| 325 | pymilvus | `milvus-io/pymilvus` | database |
| 326 | pgvector | `pgvector/pgvector-python` | database |
| 327 | sqlparse | `andialbrecht/sqlparse` | database |
| 328 | mimesis | `lk-geimfari/mimesis` | testing |
| 329 | polyfactory | `litestar-org/polyfactory` | testing |
| 330 | pytest-asyncio | `pytest-dev/pytest-asyncio` | testing |
| 331 | pytest-cov | `pytest-dev/pytest-cov` | testing |
| 332 | pytest-mock | `pytest-dev/pytest-mock` | testing |
| 333 | pytest-xdist | `pytest-dev/pytest-xdist` | testing |
| 334 | pytest-benchmark | `ionelmc/pytest-benchmark` | testing |
| 335 | pytest-bdd | `pytest-dev/pytest-bdd` | testing |
| 336 | behave | `behave/behave` | testing |
| 337 | robotframework | `robotframework/robotframework` | testing |
| 338 | locust | `locustio/locust` | testing |
| 339 | responses | `getsentry/responses` | testing |
| 340 | respx | `lundberg/respx` | testing |
| 341 | vcrpy | `kevin1024/vcrpy` | testing |
| 342 | trustme | `python-trio/trustme` | testing |
| 343 | time-machine | `adamchainz/time-machine` | testing |
| 344 | freezegun | `spulec/freezegun` | testing |
| 345 | icecream | `gruns/icecream` | dev-tools |
| 346 | objgraph | `mgedmin/objgraph` | profiling |
| 347 | memory-profiler | `pythonprofilers/memory_profiler` | profiling |
| 348 | line-profiler | `pyutils/line_profiler` | profiling |
| 349 | py-spy | `benfred/py-spy` | profiling |
| 350 | scalene | `plasma-umass/scalene` | profiling |
| 351 | viztracer | `gaogaotiantian/viztracer` | profiling |
| 352 | yappi | `sumerc/yappi` | profiling |
| 353 | pyinstrument | `joerick/pyinstrument` | profiling |
| 354 | memray | `bloomberg/memray` | profiling |
| 355 | ward | `darrenburns/ward` | testing |
| 356 | pdbpp | `pdbpp/pdbpp` | dev-tools |
| 357 | ipdb | `gotcha/ipdb` | dev-tools |
| 358 | pudb | `inducer/pudb` | dev-tools |
| 359 | devtools | `samuelcolvin/python-devtools` | dev-tools |
| 360 | psutil | `giampaolo/psutil` | system |
| 361 | sh | `amoffat/sh` | system |
| 362 | plumbum | `tomerfiliba/plumbum` | system |
| 363 | delegator | `amitt001/delegator.py` | system |
| 364 | supervisor | `Supervisor/supervisor` | system |
| 365 | circus | `circus-tent/circus` | system |
| 366 | uvloop | `MagicStack/uvloop` | async |
| 367 | curio | `dabeaz/curio` | async |
| 368 | gevent | `gevent/gevent` | async |
| 369 | eventlet | `eventlet/eventlet` | async |
| 370 | twisted | `twisted/twisted` | async |
| 371 | asgiref | `django/asgiref` | web-framework |
| 372 | whitenoise | `evansd/whitenoise` | web-framework |
| 373 | werkzeug | `pallets/werkzeug` | web-framework |
| 374 | itsdangerous | `pallets/itsdangerous` | crypto |
| 375 | markupsafe | `pallets/markupsafe` | text |
| 376 | certifi | `certifi/python-certifi` | security |
| 377 | idna | `kjd/idna` | network |
| 378 | multidict | `aio-libs/multidict` | data-structures |
| 379 | yarl | `aio-libs/yarl` | http-client |
| 380 | aiofiles | `Tinche/aiofiles` | async |
| 381 | aioresponses | `pnuckowski/aioresponses` | testing |
| 382 | httpbin | `postmanlabs/httpbin` | testing |
| 383 | moto | `getmoto/moto` | testing |
| 384 | localstack | `localstack/localstack` | testing |
| 385 | cookiecutter | `cookiecutter/cookiecutter` | dev-tools |
| 386 | copier | `copier-org/copier` | dev-tools |
| 387 | bump2version | `c4urself/bump2version` | dev-tools |
| 388 | towncrier | `twisted/towncrier` | dev-tools |
| 389 | flit | `pypa/flit` | packaging |
| 390 | pdm | `pdm-project/pdm` | packaging |
| 391 | pipx | `pypa/pipx` | packaging |
| 392 | twine | `pypa/twine` | packaging |
| 393 | build | `pypa/build` | packaging |
| 394 | wheel | `pypa/wheel` | packaging |
| 395 | maturin | `PyO3/maturin` | packaging |
| 396 | pyo3 | `PyO3/pyo3` | misc |
| 397 | cffi | `python-cffi/cffi` | misc |
| 398 | ctypes | `python/cpython` | misc |
| 399 | cython | `cython/cython` | misc |
| 400 | numba | `numba/numba` | scientific |
| 401 | geopandas | `geopandas/geopandas` | geospatial |
| 402 | shapely | `shapely/shapely` | geospatial |
| 403 | fiona | `Toblerity/Fiona` | geospatial |
| 404 | rasterio | `rasterio/rasterio` | geospatial |
| 405 | pyproj | `pyproj4/pyproj` | geospatial |
| 406 | folium | `python-visualization/folium` | geospatial |
| 407 | geopy | `geopy/geopy` | geospatial |
| 408 | osmnx | `gboeing/osmnx` | geospatial |
| 409 | h3-py | `uber/h3-py` | geospatial |
| 410 | keplergl | `keplergl/kepler.gl` | geospatial |
| 411 | pydeck | `visgl/deck.gl` | geospatial |
| 412 | geoalchemy2 | `geoalchemy/geoalchemy2` | geospatial |
| 413 | astropy | `astropy/astropy` | astronomy |
| 414 | sunpy | `sunpy/sunpy` | astronomy |
| 415 | skyfield | `skyfielders/python-skyfield` | astronomy |
| 416 | ephem | `brandon-rhodes/pyephem` | astronomy |
| 417 | healpy | `healpy/healpy` | astronomy |
| 418 | biopython | `biopython/biopython` | bioinformatics |
| 419 | pysam | `pysam-developers/pysam` | bioinformatics |
| 420 | scanpy | `scverse/scanpy` | bioinformatics |
| 421 | anndata | `scverse/anndata` | bioinformatics |
| 422 | scvi-tools | `scverse/scvi-tools` | bioinformatics |
| 423 | rdkit | `rdkit/rdkit` | chemistry |
| 424 | ase | `rosswhitfield/ase` | chemistry |
| 425 | pymatgen | `materialsproject/pymatgen` | chemistry |
| 426 | cclib | `cclib/cclib` | chemistry |
| 427 | mendeleev | `lmmentel/mendeleev` | chemistry |
| 428 | pint | `hgrecco/pint` | physics |
| 429 | uncertainties | `lmfit/uncertainties` | physics |
| 430 | openmc | `openmc-dev/openmc` | physics |
| 431 | fenics | `FEniCS/dolfinx` | physics |
| 432 | dedalus | `DedalusProject/dedalus` | physics |
| 433 | pybullet | `bulletphysics/bullet3` | robotics |
| 434 | gymnasium | `Farama-Foundation/Gymnasium` | robotics |
| 435 | stable-baselines3 | `DLR-RM/stable-baselines3` | robotics |
| 436 | sb3-contrib | `Stable-Baselines-Team/stable-baselines3-contrib` | robotics |
| 437 | imitation | `HumanCompatibleAI/imitation` | robotics |
| 438 | tianshou | `thu-ml/tianshou` | robotics |
| 439 | cleanrl | `vwxyzjn/cleanrl` | robotics |
| 440 | sample-factory | `alex-petrenko/sample-factory` | robotics |
| 441 | librosa | `librosa/librosa` | signal-processing |
| 442 | soundfile | `bastibe/python-soundfile` | signal-processing |
| 443 | sounddevice | `spatialaudio/python-sounddevice` | signal-processing |
| 444 | pydub | `jiaaro/pydub` | signal-processing |
| 445 | pedalboard | `spotify/pedalboard` | signal-processing |
| 446 | audiocraft | `facebookresearch/audiocraft` | signal-processing |
| 447 | bark | `suno-ai/bark` | signal-processing |
| 448 | coqui-tts | `coqui-ai/TTS` | signal-processing |
| 449 | whisperx | `m-bain/whisperX` | signal-processing |
| 450 | faster-whisper | `SYSTRAN/faster-whisper` | signal-processing |
| 451 | nemo-toolkit | `NVIDIA/NeMo` | signal-processing |
| 452 | detectron2 | `facebookresearch/detectron2` | computer-vision |
| 453 | mmdetection | `open-mmlab/mmdetection` | computer-vision |
| 454 | mmpose | `open-mmlab/mmpose` | computer-vision |
| 455 | mmsegmentation | `open-mmlab/mmsegmentation` | computer-vision |
| 456 | ultralytics | `ultralytics/ultralytics` | computer-vision |
| 457 | supervision | `roboflow/supervision` | computer-vision |
| 458 | kornia | `kornia/kornia` | computer-vision |
| 459 | timm | `huggingface/pytorch-image-models` | computer-vision |
| 460 | open-clip | `mlfoundations/open_clip` | computer-vision |
| 461 | segment-anything | `facebookresearch/segment-anything` | computer-vision |
| 462 | open3d | `isl-org/Open3D` | 3d-graphics |
| 463 | trimesh | `mikedh/trimesh` | 3d-graphics |
| 464 | pyvista | `pyvista/pyvista` | 3d-graphics |
| 465 | vtk | `Kitware/VTK` | 3d-graphics |
| 466 | mayavi | `enthought/mayavi` | 3d-graphics |
| 467 | pyglet | `pyglet/pyglet` | 3d-graphics |
| 468 | moderngl | `moderngl/moderngl` | 3d-graphics |
| 469 | vispy | `vispy/vispy` | 3d-graphics |
| 470 | fpdf2 | `py-pdf/fpdf2` | pdf-document |
| 471 | weasyprint | `Kozea/WeasyPrint` | pdf-document |
| 472 | xhtml2pdf | `xhtml2pdf/xhtml2pdf` | pdf-document |
| 473 | img2pdf | `josch/img2pdf` | pdf-document |
| 474 | ocrmypdf | `ocrmypdf/OCRmyPDF` | pdf-document |
| 475 | pytesseract | `madmaze/pytesseract` | pdf-document |
| 476 | easyocr | `JaidedAI/EasyOCR` | pdf-document |
| 477 | paddleocr | `PaddlePaddle/PaddleOCR` | pdf-document |
| 478 | surya | `VikParuchuri/surya` | pdf-document |
| 479 | doctr | `mindee/doctr` | pdf-document |
| 480 | unstructured | `Unstructured-IO/unstructured` | pdf-document |
| 481 | marker | `VikParuchuri/marker` | pdf-document |
| 482 | parsel | `scrapy/parsel` | web-scraping |
| 483 | selectolax | `rushter/selectolax` | web-scraping |
| 484 | h11 | `python-hyper/h11` | web-scraping |
| 485 | h2 | `python-hyper/h2` | web-scraping |
| 486 | curl-cffi | `yifeikong/curl_cffi` | web-scraping |
| 487 | cloudscraper | `VeNoMouS/cloudscraper` | web-scraping |
| 488 | mechanicalsoup | `MechanicalSoup/MechanicalSoup` | web-scraping |
| 489 | pyppeteer | `pyppeteer/pyppeteer` | web-scraping |
| 490 | crawl4ai | `unclecode/crawl4ai` | web-scraping |
| 491 | aiodns | `saghul/aiodns` | async |
| 492 | aiosmtplib | `cole/aiosmtplib` | async |
| 493 | aiobotocore | `aio-libs/aiobotocore` | async |
| 494 | great-tables | `posit-dev/great-tables` | data-validation |
| 495 | datacompy | `capitalone/datacompy` | data-validation |
| 496 | whylogs | `whylabs/whylogs` | data-validation |
| 497 | evidently | `evidentlyai/evidently` | data-validation |
| 498 | deepchecks | `deepchecks/deepchecks` | data-validation |
| 499 | alibi-detect | `SeldonDev/alibi-detect` | data-validation |
| 500 | nannyml | `NannyML/nannyml` | data-validation |
| 501 | neptune | `neptune-ai/neptune-client` | experiment-tracking |
| 502 | comet-ml | `comet-ml/comet-ml` | experiment-tracking |
| 503 | aim | `aimhubio/aim` | experiment-tracking |
| 504 | clearml | `allegroai/clearml` | experiment-tracking |
| 505 | determined | `determined-ai/determined` | experiment-tracking |
| 506 | bentoml | `bentoml/BentoML` | model-serving |
| 507 | mlserver | `SeldonDev/MLServer` | model-serving |
| 508 | torchserve | `pytorch/serve` | model-serving |
| 509 | litserve | `Lightning-AI/LitServe` | model-serving |
| 510 | fastembed | `qdrant/fastembed` | model-serving |
| 511 | semantic-kernel | `microsoft/semantic-kernel` | llm-tools |
| 512 | haystack | `deepset-ai/haystack` | llm-tools |
| 513 | txtai | `neuml/txtai` | llm-tools |
| 514 | ragas | `explodinggradients/ragas` | llm-tools |
| 515 | phoenix-arize | `Arize-ai/phoenix` | llm-tools |
| 516 | guardrails-ai | `guardrails-ai/guardrails` | llm-tools |
| 517 | nemoguardrails | `NVIDIA/NeMo-Guardrails` | llm-tools |
| 518 | llm-guard | `protectai/llm-guard` | llm-tools |
| 519 | hamilton | `DAGWorks-Inc/hamilton` | workflow |
| 520 | metaflow | `Netflix/metaflow` | workflow |
| 521 | flyte | `flyteorg/flytekit` | workflow |
| 522 | zenml | `zenml-io/zenml` | workflow |
| 523 | kedro | `kedro-org/kedro` | workflow |
| 524 | ploomber | `ploomber/ploomber` | workflow |
| 525 | soda-core | `sodadata/soda-core` | data-engineering |
| 526 | dbt-core | `dbt-labs/dbt-core` | data-engineering |
| 527 | sqlmesh | `TobikoData/sqlmesh` | data-engineering |
| 528 | sqlglot | `tobymao/sqlglot` | data-engineering |
| 529 | ibis | `ibis-project/ibis` | data-engineering |
| 530 | fugue | `fugue-project/fugue` | data-engineering |
| 531 | datafusion | `apache/datafusion-python` | data-engineering |
| 532 | connectorx | `sfu-db/connector-x` | data-engineering |
| 533 | deltalake | `delta-io/delta-rs` | data-engineering |
| 534 | pygame | `pygame/pygame` | game-development |
| 535 | arcade | `pythonarcade/arcade` | game-development |
| 536 | ursina | `pokepetter/ursina` | game-development |
| 537 | panda3d | `panda3d/panda3d` | game-development |
| 538 | manim | `ManimCommunity/manim` | animation |
| 539 | moviepy | `Zulko/moviepy` | video-processing |
| 540 | ffmpeg-python | `kkroening/ffmpeg-python` | video-processing |
| 541 | vidgear | `abhiTronix/vidgear` | video-processing |
| 542 | av | `PyAV-Org/PyAV` | video-processing |
| 543 | pyautogui | `asweigart/pyautogui` | automation |
| 544 | keyboard | `boppreh/keyboard` | automation |
| 545 | pyperclip | `asweigart/pyperclip` | automation |
| 546 | pyqt5 | `PyQt5/PyQt` | gui |
| 547 | pyside6 | `qt/qtforpython` | gui |
| 548 | kivy | `kivy/kivy` | gui |
| 549 | wxpython | `wxWidgets/Phoenix` | gui |
| 550 | dearpygui | `hoffstadt/DearPyGui` | gui |
| 551 | flet | `flet-dev/flet` | gui |
| 552 | customtkinter | `TomSchimansky/CustomTkinter` | gui |
| 553 | mpmath | `mpmath/mpmath` | mathematics |
| 554 | gekko | `BYU-PRISM/GEKKO` | mathematics |
| 555 | cvxpy | `cvxpy/cvxpy` | mathematics |
| 556 | pyomo | `Pyomo/pyomo` | mathematics |
| 557 | scikit-image | `scikit-image/scikit-image` | image-processing |
| 558 | imageio | `imageio/imageio` | image-processing |
| 559 | scikit-optimize | `scikit-optimize/scikit-optimize` | optimization |
| 560 | nevergrad | `facebookresearch/nevergrad` | optimization |
| 561 | hyperopt | `hyperopt/hyperopt` | optimization |
| 562 | pygmo | `esa/pygmo2` | optimization |
| 563 | deap | `DEAP/deap` | optimization |
| 564 | pybind11 | `pybind/pybind11` | performance |
| 565 | nuitka | `Nuitka/Nuitka` | performance |
| 566 | pyinstaller | `pyinstaller/pyinstaller` | packaging |
| 567 | briefcase | `beeware/briefcase` | packaging |
| 568 | cx-freeze | `marcelotduarte/cx_Freeze` | packaging |
| 569 | python-igraph | `igraph/python-igraph` | graph |
| 570 | graph-tool | `count0/graph-tool` | graph |
| 571 | pyvis | `WestHealth/pyvis` | graph |
| 572 | stanza | `stanfordnlp/stanza` | nlp |
| 573 | textblob | `sloria/TextBlob` | nlp |
| 574 | sumy | `miso-belica/sumy` | nlp |
| 575 | newspaper3k | `codelucas/newspaper` | nlp |
| 576 | trafilatura | `adbar/trafilatura` | nlp |
| 577 | ydata-profiling | `ydataai/ydata-profiling` | data-quality |
| 578 | sweetviz | `fbdesignpro/sweetviz` | data-quality |
| 579 | missingno | `ResidentMario/missingno` | data-quality |
| 580 | prophet | `facebook/prophet` | time-series |
| 581 | statsforecast | `Nixtla/statsforecast` | time-series |
| 582 | neuralforecast | `Nixtla/neuralforecast` | time-series |
| 583 | sktime | `sktime/sktime` | time-series |
| 584 | tslearn | `tslearn-team/tslearn` | time-series |
| 585 | darts | `unit8co/darts` | time-series |
| 586 | tsfresh | `blue-yonder/tsfresh` | time-series |
| 587 | arch | `bashtage/arch` | finance |
| 588 | zipline-reloaded | `stefan-jansen/zipline-reloaded` | finance |
| 589 | backtrader | `mementum/backtrader` | finance |
| 590 | yfinance | `ranaroussi/yfinance` | finance |
| 591 | ta-lib | `TA-Lib/ta-lib-python` | finance |
| 592 | quantlib | `lballabio/QuantLib-SWIG` | finance |
| 593 | pyqt6 | `riverbank/pyqt6` | gui |
| 594 | pygobject | `GNOME/pygobject` | gui |
| 595 | toga | `beeware/toga` | gui |
| 596 | pywebview | `nicegui-org/pywebview` | gui |
| 597 | eel | `python-eel/Eel` | gui |
| 598 | pywebio | `pywebio/PyWebIO` | gui |
| 599 | ttkbootstrap | `israel-dryer/ttkbootstrap` | gui |
| 600 | pyxel | `kitao/pyxel` | game-dev |
| 601 | ppb | `ppb/pursuedpybear` | game-dev |
| 602 | pyserial | `pyserial/pyserial` | embedded-hardware |
| 603 | pyusb | `pyusb/pyusb` | embedded-hardware |
| 604 | gpiozero | `gpiozero/gpiozero` | embedded-hardware |
| 605 | adafruit-blinka | `adafruit/Adafruit_Blinka` | embedded-hardware |
| 606 | spidev | `doceme/py-spidev` | embedded-hardware |
| 607 | smbus2 | `kplindegaard/smbus2` | embedded-hardware |
| 608 | hidapi | `trezor/cython-hidapi` | embedded-hardware |
| 609 | pyocd | `pyocd/pyOCD` | embedded-hardware |
| 610 | esptool | `espressif/esptool` | embedded-hardware |
| 611 | platformio-core | `platformio/platformio-core` | embedded-hardware |
| 612 | scapy | `secdev/scapy` | networking |
| 613 | dpkt | `kbandla/dpkt` | networking |
| 614 | pyshark | `KimiNewt/pyshark` | networking |
| 615 | impacket | `fortra/impacket` | networking |
| 616 | sniffio | `python-trio/sniffio` | networking |
| 617 | pyinfra | `pyinfra-dev/pyinfra` | devops |
| 618 | mitogen | `mitogen-hq/mitogen` | devops |
| 619 | molecule | `ansible/molecule` | devops |
| 620 | testinfra | `pytest-dev/pytest-testinfra` | devops |
| 621 | or-tools | `google/or-tools` | math-optimization |
| 622 | pulp | `coin-or/pulp` | math-optimization |
| 623 | casadi | `casadi/casadi` | math-optimization |
| 624 | pymoo | `anyoptimization/pymoo` | math-optimization |
| 625 | ax-platform | `facebook/Ax` | math-optimization |
| 626 | botorch | `pytorch/botorch` | math-optimization |
| 627 | gpytorch | `cornellius-gp/gpytorch` | math-optimization |
| 628 | allennlp | `allenai/allennlp` | nlp-advanced |
| 629 | fairseq | `facebookresearch/fairseq` | nlp-advanced |
| 630 | ctranslate2 | `OpenNMT/CTranslate2` | model-inference |
| 631 | onnxruntime | `microsoft/onnxruntime` | model-inference |
| 632 | openvino | `openvinotoolkit/openvino` | model-inference |
| 633 | tvm | `apache/tvm` | model-inference |
| 634 | deepsparse | `neuralmagic/deepsparse` | model-inference |
| 635 | sparseml | `neuralmagic/sparseml` | model-inference |
| 636 | neural-compressor | `intel/neural-compressor` | model-inference |
| 637 | mahotas | `luispedro/mahotas` | image-processing |
| 638 | rawpy | `letmaik/rawpy` | image-processing |
| 639 | colour-science | `colour-science/colour` | image-processing |
| 640 | colorama | `tartley/colorama` | terminal-utils |
| 641 | flask-dance | `singingwolfboy/flask-dance` | web-auth |
| 642 | django-oauth-toolkit | `jazzband/django-oauth-toolkit` | web-auth |
| 643 | django-two-factor-auth | `jazzband/django-two-factor-auth` | web-auth |
| 644 | pyotp | `pyauth/pyotp` | web-auth |
| 645 | fido2 | `Yubico/python-fido2` | web-auth |
| 646 | django-crispy-forms | `django-crispy-forms/django-crispy-forms` | web-utils |
| 647 | django-tables2 | `jieter/django-tables2` | web-utils |
| 648 | django-import-export | `django-import-export/django-import-export` | web-utils |
| 649 | django-grappelli | `sehmaschine/django-grappelli` | web-utils |
| 650 | django-unfold | `unfoldadmin/django-unfold` | web-utils |
| 651 | flask-admin | `flask-admin/flask-admin` | web-utils |
| 652 | flask-security | `Flask-Middleware/flask-security` | web-utils |
| 653 | flask-wtf | `wtforms/flask-wtf` | web-utils |
| 654 | wtforms | `wtforms/wtforms` | web-utils |
| 655 | flask-limiter | `alisaifee/flask-limiter` | web-utils |
| 656 | flask-session | `pallets-eco/flask-session` | web-utils |
| 657 | flask-marshmallow | `marshmallow-code/flask-marshmallow` | web-utils |
| 658 | daphne | `django/daphne` | web-utils |
| 659 | django-celery-results | `celery/django-celery-results` | web-utils |
| 660 | django-silk | `jazzband/django-silk` | web-utils |
| 661 | django-cachalot | `noripyt/django-cachalot` | web-utils |
| 662 | django-redis | `jazzband/django-redis` | web-utils |
| 663 | django-health-check | `revsys/django-health-check` | web-utils |
| 664 | django-anymail | `anymail/django-anymail` | web-utils |
| 665 | schemathesis | `schemathesis/schemathesis` | api-tools |
| 666 | openapi-spec-validator | `python-openapi/openapi-spec-validator` | api-tools |
| 667 | flasgger | `flasgger/flasgger` | api-tools |
| 668 | drf-spectacular | `tfranzel/drf-spectacular` | api-tools |
| 669 | drf-yasg | `axnsan12/drf-yasg` | api-tools |
| 670 | email-validator | `JoshData/python-email-validator` | api-tools |
| 671 | rocketry | `Miksus/rocketry` | task-scheduling |
| 672 | vectorbt | `polakowo/vectorbt` | finance |
| 673 | empyrical | `quantopian/empyrical` | finance |
| 674 | pyfolio | `quantopian/pyfolio` | finance |
| 675 | alphalens | `quantopian/alphalens` | finance |
| 676 | ccxt | `ccxt/ccxt` | finance |
| 677 | freqtrade | `freqtrade/freqtrade` | finance |
| 678 | nautilus-trader | `nautechsystems/nautilus_trader` | finance |
| 679 | pydicom | `pydicom/pydicom` | healthcare |
| 680 | nibabel | `nipy/nibabel` | healthcare |
| 681 | nilearn | `nilearn/nilearn` | healthcare |
| 682 | monai | `Project-MONAI/MONAI` | healthcare |
| 683 | medpy | `loli/medpy` | healthcare |
| 684 | hl7 | `johnpaulett/python-hl7` | healthcare |
| 685 | jupyterlab | `jupyterlab/jupyterlab` | education |
| 686 | ipython | `ipython/ipython` | education |
| 687 | ipywidgets | `jupyter-widgets/ipywidgets` | education |
| 688 | nbconvert | `jupyter/nbconvert` | education |
| 689 | nbformat | `jupyter/nbformat` | education |
| 690 | papermill | `nteract/papermill` | education |
| 691 | voila | `voila-dashboards/voila` | education |
| 692 | jupyterhub | `jupyterhub/jupyterhub` | education |
| 693 | nbgrader | `jupyter/nbgrader` | education |
| 694 | mitmproxy | `mitmproxy/mitmproxy` | networking |
| 695 | cupy | `cupy/cupy` | performance |
| 696 | sage | `sagemath/sage` | math-symbolic |
| 697 | construct | `construct/construct` | binary-parsing |
| 698 | bitstring | `scott-griffiths/bitstring` | binary-parsing |
| 699 | kaitaistruct | `kaitai-io/kaitai_struct_python_runtime` | binary-parsing |
| 700 | glom | `mahmoud/glom` | utilities |
| 701 | pytube | `pytube/pytube` | media |
| 702 | yt-dlp | `yt-dlp/yt-dlp` | media |
| 703 | mutagen | `quodlibet/mutagen` | media |
| 704 | parameterized | `wolever/parameterized` | testing |
| 705 | dirty-equals | `samuelcolvin/dirty-equals` | testing |
| 706 | django-treebeard | `django-treebeard/django-treebeard` | web-utils |
| 707 | typeguard | `agronholm/typeguard` | type-checking |
| 708 | beartype | `beartype/beartype` | type-checking |
| 709 | typing-extensions | `python/typing_extensions` | type-checking |
| 710 | typing-inspect | `ilevkivskyi/typing_inspect` | type-checking |
| 711 | monkeytype | `Instagram/MonkeyType` | type-checking |
| 712 | pytype | `google/pytype` | type-checking |
| 713 | phantom-types | `antonagestam/phantom-types` | type-checking |
| 714 | pytest-django | `pytest-dev/pytest-django` | testing |
| 715 | pytest-flask | `pytest-dev/pytest-flask` | testing |
| 716 | pytest-sugar | `Teemu/pytest-sugar` | testing |
| 717 | pytest-randomly | `pytest-dev/pytest-randomly` | testing |
| 718 | pytest-timeout | `pytest-dev/pytest-timeout` | testing |
| 719 | pytest-rerunfailures | `pytest-dev/pytest-rerunfailures` | testing |
| 720 | pytest-lazy-fixture | `TvoroG/pytest-lazy-fixture` | testing |
| 721 | pytest-env | `MobileDynasty/pytest-env` | testing |
| 722 | pytest-factoryboy | `pytest-dev/pytest-factoryboy` | testing |
| 723 | pytest-recording | `kiwicom/pytest-recording` | testing |
| 724 | syrupy | `toptal/syrupy` | testing |
| 725 | inline-snapshot | `15r10nk/inline-snapshot` | testing |
| 726 | pydantic-factories | `litestar-org/pydantic-factories` | testing |
| 727 | pytest-playwright | `microsoft/playwright-pytest` | testing |
| 728 | setuptools-scm | `pypa/setuptools-scm` | packaging |
| 729 | commitizen | `commitizen-tools/commitizen` | packaging |
| 730 | scriv | `nedbat/scriv` | packaging |
| 731 | python-semantic-release | `python-semantic-release/python-semantic-release` | packaging |
| 732 | cibuildwheel | `pypa/cibuildwheel` | packaging |
| 733 | shiv | `linkedin/shiv` | packaging |
| 734 | pex | `pex-tool/pex` | packaging |
| 735 | datamodel-code-generator | `koxudaxi/datamodel-code-generator` | code-generation |
| 736 | sqlacodegen | `agronholm/sqlacodegen` | code-generation |
| 737 | openapi-python-client | `openapi-generators/openapi-python-client` | code-generation |
| 738 | grpcio-tools | `grpc/grpc` | code-generation |
| 739 | python-decouple | `HBNetwork/python-decouple` | config |
| 740 | environs | `sloria/environs` | config |
| 741 | strictyaml | `crdoconnor/strictyaml` | config |
| 742 | omegaconf | `omry/omegaconf` | config |
| 743 | confuse | `beetbox/confuse` | config |
| 744 | goodconf | `lincolnloop/goodconf` | config |
| 745 | cleo | `python-poetry/cleo` | cli |
| 746 | cement | `datafolklabs/cement` | cli |
| 747 | cliff | `openstack/cliff` | cli |
| 748 | plac | `ialbert/plac` | cli |
| 749 | docopt | `docopt/docopt` | cli |
| 750 | argcomplete | `kislyuk/argcomplete` | cli |
| 751 | shtab | `iterative/shtab` | cli |
| 752 | tomlkit | `sdispater/tomlkit` | data-formats |
| 753 | ruamel-yaml | `ruamel/yaml` | data-formats |
| 754 | xmltodict | `martinblech/xmltodict` | data-formats |
| 755 | defusedxml | `tiran/defusedxml` | data-formats |
| 756 | brotli | `google/brotli` | compression |
| 757 | zstandard | `indygreg/python-zstandard` | compression |
| 758 | lz4 | `python-lz4/python-lz4` | compression |
| 759 | cramjam | `milesgranger/cramjam` | compression |
| 760 | msgspec | `jcrist/msgspec` | data-validation |
| 761 | lark | `lark-parser/lark` | parsing |
| 762 | pyparsing | `pyparsing/pyparsing` | parsing |
| 763 | parso | `davidhalter/parso` | parsing |
| 764 | tree-sitter | `tree-sitter/py-tree-sitter` | parsing |
| 765 | libcst | `Instagram/LibCST` | code-transformation |
| 766 | rope | `python-rope/rope` | code-transformation |
| 767 | jedi | `davidhalter/jedi` | code-analysis |
| 768 | redbaron | `PyCQA/redbaron` | code-transformation |
| 769 | bowler | `facebookincubator/Bowler` | code-transformation |
| 770 | autopep8 | `hhatto/autopep8` | code-formatting |
| 771 | yapf | `google/yapf` | code-formatting |
| 772 | pyink | `google/pyink` | code-formatting |
| 773 | docformatter | `PyCQA/docformatter` | code-formatting |
| 774 | pydocstyle | `PyCQA/pydocstyle` | code-quality |
| 775 | interrogate | `econchick/interrogate` | code-quality |
| 776 | vulture | `jendrikseipp/vulture` | code-quality |
| 777 | dead | `asottile/dead` | code-quality |
| 778 | importlib-metadata | `python/importlib_metadata` | stdlib-backport |
| 779 | importlib-resources | `python/importlib_resources` | stdlib-backport |
| 780 | google-cloud-bigquery | `googleapis/python-bigquery` | cloud |
| 781 | google-cloud-pubsub | `googleapis/python-pubsub` | cloud |
| 782 | google-cloud-aiplatform | `googleapis/python-aiplatform` | cloud |
| 783 | google-generativeai | `google/generative-ai-python` | cloud |
| 784 | azure-identity | `Azure/azure-sdk-for-python` | cloud |
| 785 | azure-cosmos | `Azure/azure-sdk-for-python` | cloud |
| 786 | azure-servicebus | `Azure/azure-sdk-for-python` | cloud |
| 787 | azure-keyvault | `Azure/azure-sdk-for-python` | cloud |
| 788 | aws-lambda-powertools | `aws-powertools/powertools-lambda-python` | cloud |
| 789 | boto3-stubs | `youtype/mypy_boto3_builder` | cloud |
| 790 | opentelemetry-python | `open-telemetry/opentelemetry-python` | monitoring |
| 791 | ddtrace | `DataDog/dd-trace-py` | monitoring |
| 792 | elastic-apm | `elastic/apm-agent-python` | monitoring |
| 793 | prometheus-fastapi-instrumentator | `trallnag/prometheus-fastapi-instrumentator` | monitoring |
| 794 | django-prometheus | `korfuri/django-prometheus` | monitoring |
| 795 | flower | `mher/flower` | monitoring |
| 796 | detect-secrets | `Yelp/detect-secrets` | security |
| 797 | python-gnupg | `vsajip/python-gnupg` | security |
| 798 | argon2-cffi | `hynek/argon2-cffi` | security |
| 799 | bleach | `mozilla/bleach` | security |
| 800 | nh3 | `messense/nh3` | security |
| 801 | pip-audit | `pypa/pip-audit` | security |
| 802 | goose3 | `goose3/goose3` | web-scraping |
| 803 | readability-lxml | `buriy/python-readability` | web-scraping |
| 804 | html2text | `Alir3z4/html2text` | web-scraping |
| 805 | markdownify | `matthewwithanm/python-markdownify` | web-scraping |
| 806 | html5lib | `html5lib/html5lib-python` | web-scraping |
| 807 | cssselect | `scrapy/cssselect` | web-scraping |
| 808 | extruct | `scrapinghub/extruct` | web-scraping |
| 809 | rdflib | `RDFLib/rdflib` | data-formats |
| 810 | hypercorn | `pgjones/hypercorn` | deployment |
| 811 | granian | `emmett-framework/granian` | deployment |
| 812 | mangum | `jordanerr/mangum` | deployment |
| 813 | chalice | `aws/chalice` | deployment |
| 814 | zappa | `zappa/Zappa` | deployment |
| 815 | troposphere | `cloudtools/troposphere` | infrastructure |
| 816 | humanize | `jmoiron/humanize` | utilities |
| 817 | inflect | `jaraco/inflect` | utilities |
| 818 | titlecase | `ppannuto/python-titlecase` | utilities |
| 819 | phonenumbers | `daviddrysdale/python-phonenumbers` | utilities |
| 820 | pycountry | `flyingcircusio/pycountry` | utilities |
| 821 | send2trash | `arsenetar/send2trash` | utilities |
| 822 | platformdirs | `platformdirs/platformdirs` | utilities |
| 823 | pathspec | `cpburnz/python-pathspec` | utilities |
| 824 | wcmatch | `facelessuser/wcmatch` | utilities |
| 825 | shortuuid | `skorokithakis/shortuuid` | utilities |
| 826 | ulid-py | `mdomke/python-ulid` | utilities |
| 827 | python-barcode | `WhyNotHugo/python-barcode` | utilities |
| 828 | qrcode | `lincolnloop/python-qrcode` | utilities |
| 829 | segno | `heuer/segno` | utilities |
| 830 | cairosvg | `Kozea/CairoSVG` | graphics |
| 831 | svglib | `deeplook/svglib` | graphics |
| 832 | drawsvg | `cduck/drawsvg` | graphics |
| 833 | cruft | `cruft/cruft` | developer-tools |
| 834 | editorconfig | `editorconfig/editorconfig-core-py` | developer-tools |
| 835 | sshtunnel | `pahaz/sshtunnel` | networking |
| 836 | dnspython | `rthalley/dnspython` | networking |
| 837 | whenever | `ariebovenberg/whenever` | datetime |
| 838 | cashews | `krukov/cashews` | caching |
| 839 | python-json-logger | `madzak/python-json-logger` | logging |
| 840 | picologging | `microsoft/picologging` | logging |
| 841 | asgi-cors | `simonw/asgi-cors` | web-middleware |
| 842 | starlette-admin | `jowilf/starlette-admin` | web-middleware |
| 843 | fastapi-users | `fastapi-users/fastapi-users` | web-middleware |
| 844 | fastapi-cache | `long2ice/fastapi-cache` | web-middleware |
| 845 | fastapi-limiter | `long2ice/fastapi-limiter` | web-middleware |
| 846 | fastapi-pagination | `uriyyo/fastapi-pagination` | web-middleware |
| 847 | fastapi-mail | `sabuhish/fastapi-mail` | web-middleware |
| 848 | fastapi-jwt-auth | `IndominusByte/fastapi-jwt-auth` | web-middleware |
| 849 | sqladmin | `aminalaee/sqladmin` | web-middleware |
| 850 | piccolo-admin | `piccolo-orm/piccolo_admin` | web-middleware |
| 851 | django-polymorphic | `jazzband/django-polymorphic` | django |
| 852 | django-reversion | `etianen/django-reversion` | django |
| 853 | django-simple-history | `jazzband/django-simple-history` | django |
| 854 | django-auditlog | `jazzband/django-auditlog` | django |
| 855 | django-activity-stream | `justquick/django-activity-stream` | django |
| 856 | django-notifications-hq | `django-notifications/django-notifications` | django |
| 857 | django-pghistory | `Opus10/django-pghistory` | django |
| 858 | django-lifecycle | `rsinger86/django-lifecycle` | django |
| 859 | django-model-utils | `jazzband/django-model-utils` | django |
| 860 | django-fsm | `viewflow/django-fsm` | django |
| 861 | django-money | `django-money/django-money` | django |
| 862 | django-countries | `SmileyChris/django-countries` | django |
| 863 | django-phonenumber-field | `stefanfoulis/django-phonenumber-field` | django |
| 864 | django-taggit | `jazzband/django-taggit` | django |
| 865 | django-watson | `etianen/django-watson` | django |
| 866 | django-haystack | `django-haystack/django-haystack` | django |
| 867 | django-elasticsearch-dsl | `django-es/django-elasticsearch-dsl` | django |
| 868 | django-ckeditor | `django-ckeditor/django-ckeditor` | django |
| 869 | django-summernote | `summernote/django-summernote` | django |
| 870 | django-tinymce | `jazzband/django-tinymce` | django |
| 871 | django-markdownx | `neutronX/django-markdownx` | django |
| 872 | pytest-freezegun | `ktosber/pytest-freezegun` | testing |
| 873 | pytest-repeat | `pytest-dev/pytest-repeat` | testing |
| 874 | pytest-ordering | `ftobia/pytest-ordering` | testing |
| 875 | pytest-parallel | `browsertron/pytest-parallel` | testing |
| 876 | pytest-html | `pytest-dev/pytest-html` | testing |
| 877 | pytest-metadata | `pytest-dev/pytest-metadata` | testing |
| 878 | allure-pytest | `allure-framework/allure-python` | testing |
| 879 | pytest-selenium | `pytest-dev/pytest-selenium` | testing |
| 880 | pytest-base-url | `pytest-dev/pytest-base-url` | testing |
| 881 | tavern | `taverntesting/tavern` | testing |
| 882 | openapi-core | `python-openapi/openapi-core` | testing |
| 883 | tiktoken | `openai/tiktoken` | nlp |
| 884 | sentencepiece | `google/sentencepiece` | nlp |
| 885 | sacrebleu | `mjpost/sacrebleu` | nlp |
| 886 | rouge-score | `google-research/google-research` | nlp |
| 887 | evaluate | `huggingface/evaluate` | nlp |
| 888 | neuralprophet | `ourownstory/neural_prophet` | time-series |
| 889 | stumpy | `TDAmeritrade/stumpy` | time-series |
| 890 | pyod | `yzhao062/pyod` | anomaly-detection |
| 891 | alibi | `SeldonIO/alibi` | explainability |
| 892 | shap | `shap/shap` | explainability |
| 893 | lime | `marcotcr/lime` | explainability |
| 894 | eli5 | `eli5-org/eli5` | explainability |
| 895 | captum | `pytorch/captum` | explainability |
| 896 | interpret | `interpretml/interpret` | explainability |
| 897 | dalex | `ModelOriented/DALEX` | explainability |
| 898 | fairlearn | `fairlearn/fairlearn` | fairness |
| 899 | aif360 | `Trusted-AI/AIF360` | fairness |
| 900 | responsibleai | `microsoft/responsible-ai-toolbox` | fairness |
| 901 | imageio-ffmpeg | `imageio/imageio-ffmpeg` | video-processing |
| 902 | pdf2image | `Belval/pdf2image` | pdf-document |
| 903 | wand | `emcconville/wand` | image-processing |
| 904 | svgwrite | `mozman/svgwrite` | graphics |
| 905 | vpype | `abey79/vpype` | graphics |
| 906 | decord | `dmlc/decord` | video-processing |
| 907 | klein | `twisted/klein` | web-framework |
| 908 | treq | `twisted/treq` | http-client |
| 909 | autobahn | `crossbario/autobahn-python` | protocol |
| 910 | crossbar | `crossbario/crossbar` | protocol |
| 911 | nameko | `nameko/nameko` | microservices |
| 912 | grpclib | `vmagamedov/grpclib` | protocol |
| 913 | purerpc | `standy66/purerpc` | protocol |
| 914 | exceptiongroup | `agronholm/exceptiongroup` | async |
| 915 | asyncer | `tiangolo/asyncer` | async |
| 916 | async-timeout | `aio-libs/async-timeout` | async |
| 917 | async-lru | `aio-libs/async-lru` | async |
| 918 | async-generator | `python-trio/async_generator` | async |
| 919 | doit | `pydoit/doit` | build |
| 920 | scons | `SCons/scons` | build |
| 921 | meson-python | `mesonbuild/meson-python` | build |
| 922 | scikit-build | `scikit-build/scikit-build` | build |
| 923 | scikit-build-core | `scikit-build/scikit-build-core` | build |
| 924 | nanobind | `wjakob/nanobind` | build |
| 925 | codon | `exaloop/codon` | compiler |
| 926 | records | `kennethreitz/records` | data-access |
| 927 | dataset | `pudo/dataset` | data-access |
| 928 | tablib | `jazzband/tablib` | data-access |
| 929 | rows | `turicas/rows` | data-access |
| 930 | agate | `wireservice/agate` | data-access |
| 931 | csvkit | `wireservice/csvkit` | data-access |
| 932 | petl | `petl-developers/petl` | data-access |
| 933 | intake | `intake/intake` | data-access |
| 934 | fsspec | `fsspec/filesystem_spec` | data-access |
| 935 | s3fs | `fsspec/s3fs` | data-access |
| 936 | gcsfs | `fsspec/gcsfs` | data-access |
| 937 | adlfs | `fsspec/adlfs` | data-access |
| 938 | smart-open | `piskvorky/smart_open` | data-access |
| 939 | cloudpathlib | `drivendataorg/cloudpathlib` | data-access |
| 940 | whoosh | `mchaput/whoosh` | search |
| 941 | tantivy-py | `quickwit-oss/tantivy-py` | search |
| 942 | meilisearch | `meilisearch/meilisearch-python` | search |
| 943 | typesense | `typesense/typesense-python` | search |
| 944 | elasticsearch-dsl | `elastic/elasticsearch-dsl-py` | search |
| 945 | opensearch-py | `opensearch-project/opensearch-py` | search |
| 946 | pysolr | `django-haystack/pysolr` | search |
| 947 | waitress | `Pylons/waitress` | web-server |
| 948 | bjoern | `jonashaag/bjoern` | web-server |
| 949 | meinheld | `mopemope/meinheld` | web-server |
| 950 | a2wsgi | `abersheeran/a2wsgi` | web-server |
| 951 | starlette-context | `tomwojcik/starlette-context` | web-server |
| 952 | emoji | `carpedm20/emoji` | utilities |
| 953 | appdirs | `ActiveState/appdirs` | utilities |
| 954 | nanoid | `puyuan/py-nanoid` | utilities |
| 955 | rapidfuzz | `maxbachmann/RapidFuzz` | text |
| 956 | thefuzz | `seatgeek/thefuzz` | text |
| 957 | jellyfish | `jamesturk/jellyfish` | text |
| 958 | regex | `mrabarnett/mrab-regex` | text |
| 959 | markdown | `Python-Markdown/markdown` | text |
| 960 | mistune | `lepture/mistune` | text |
| 961 | markdown-it-py | `executablebooks/markdown-it-py` | text |
| 962 | python-Levenshtein | `maxbachmann/Levenshtein` | text |
| 963 | mdformat | `hukkin/mdformat` | text |
| 964 | bidict | `jab/bidict` | data-structures |
| 965 | python-benedict | `fabiocaccamo/python-benedict` | utilities |
| 966 | box | `cdgriffith/Box` | utilities |
| 967 | sphinx-autodoc-typehints | `tox-dev/sphinx-autodoc-typehints` | documentation |
| 968 | sphinx-rtd-theme | `readthedocs/sphinx_rtd_theme` | documentation |
| 969 | mkdocs-material | `squidfunk/mkdocs-material` | documentation |
| 970 | pdoc | `mitmproxy/pdoc` | documentation |
| 971 | numpydoc | `numpy/numpydoc` | documentation |
| 972 | griffe | `mkdocstrings/griffe` | documentation |
| 973 | mike | `jimporter/mike` | documentation |
| 974 | isodate | `gweis/isodate` | datetime |
| 975 | cachecontrol | `psf/cachecontrol` | caching |
| 976 | addict | `mewwts/addict` | utilities |
| 977 | executing | `alexmojaki/executing` | dev-tools |
| 978 | asttokens | `gristlabs/asttokens` | dev-tools |
| 979 | stack-data | `alexmojaki/stack-data` | dev-tools |
| 980 | pygwalker | `Kanaries/pygwalker` | visualization |
| 981 | hiplot | `facebookresearch/hiplot` | visualization |
| 982 | pillow-simd | `uploadcare/pillow-simd` | image-processing |
| 983 | pennylane | `PennyLaneAI/pennylane` | quantum-computing |
| 984 | qiskit | `Qiskit/qiskit` | quantum-computing |
| 985 | cirq | `quantumlib/Cirq` | quantum-computing |
| 986 | tryceratops | `guilatrova/tryceratops` | code-quality |
| 987 | flake8-bugbear | `PyCQA/flake8-bugbear` | code-quality |
| 988 | result | `rustedpy/result` | functional |
| 989 | option | `MaT1g3R/option` | functional |
| 990 | pynacl | `pyca/pynacl` | crypto |
| 991 | bcrypt | `pyca/bcrypt` | crypto |
| 992 | parameterize | `wolever/parameterized` | testing |
| 993 | deepdiff | `seperman/deepdiff` | utilities |
| 994 | dictdiffer | `inveniosoftware/dictdiffer` | utilities |
| 995 | blessed | `jquast/blessed` | tui |
| 996 | curses-menu | `pmbarrett314/curses-menu` | tui |
| 997 | questionary | `tmbo/questionary` | cli |
| 998 | inquirer | `magmax/python-inquirer` | cli |
| 999 | alive-progress | `rsalmei/alive-progress` | cli |
| 1000 | halo | `manrajgrover/halo` | cli |

### JS/TS Packages (1000 projects, 123 categories)

| # | Name | Repo | Category |
|---|------|------|----------|
| 1 | react | `facebook/react` | ui-library |
| 2 | vue | `vuejs/core` | ui-library |
| 3 | angular | `angular/angular` | framework |
| 4 | svelte | `sveltejs/svelte` | ui-library |
| 5 | solid | `solidjs/solid` | ui-library |
| 6 | preact | `preactjs/preact` | ui-library |
| 7 | qwik | `QwikDev/qwik` | framework |
| 8 | lit | `lit/lit` | ui-library |
| 9 | next.js | `vercel/next.js` | meta-framework |
| 10 | nuxt | `nuxt/nuxt` | meta-framework |
| 11 | remix | `remix-run/remix` | meta-framework |
| 12 | astro | `withastro/astro` | meta-framework |
| 13 | gatsby | `gatsbyjs/gatsby` | meta-framework |
| 14 | sveltekit | `sveltejs/kit` | meta-framework |
| 15 | fresh | `denoland/fresh` | meta-framework |
| 16 | hono | `honojs/hono` | server |
| 17 | express | `expressjs/express` | server |
| 18 | fastify | `fastify/fastify` | server |
| 19 | koa | `koajs/koa` | server |
| 20 | nestjs | `nestjs/nest` | framework |
| 21 | adonis | `adonisjs/core` | framework |
| 22 | hapi | `hapijs/hapi` | server |
| 23 | h3 | `unjs/h3` | server |
| 24 | nitro | `unjs/nitro` | server |
| 25 | trpc | `trpc/trpc` | rpc |
| 26 | zod | `colinhacks/zod` | schema |
| 27 | yup | `jquense/yup` | validation |
| 28 | joi | `hapijs/joi` | validation |
| 29 | ajv | `ajv-validator/ajv` | validation |
| 30 | valibot | `fabian-hiller/valibot` | schema |
| 31 | typebox | `sinclairzx81/typebox` | schema |
| 32 | arktype | `arktypeio/arktype` | schema |
| 33 | effect | `Effect-TS/effect` | utility |
| 34 | fp-ts | `gcanti/fp-ts` | utility |
| 35 | ramda | `ramda/ramda` | utility |
| 36 | lodash | `lodash/lodash` | utility |
| 37 | date-fns | `date-fns/date-fns` | date-time |
| 38 | dayjs | `iamkun/dayjs` | date-time |
| 39 | luxon | `moment/luxon` | date-time |
| 40 | moment | `moment/moment` | date-time |
| 41 | axios | `axios/axios` | http-client |
| 42 | got | `sindresorhus/got` | http-client |
| 43 | ky | `sindresorhus/ky` | http-client |
| 44 | node-fetch | `node-fetch/node-fetch` | http-client |
| 45 | undici | `nodejs/undici` | http-client |
| 46 | cheerio | `cheeriojs/cheerio` | scraping |
| 47 | puppeteer | `puppeteer/puppeteer` | browser |
| 48 | playwright | `microsoft/playwright` | browser |
| 49 | prisma | `prisma/prisma` | orm |
| 50 | drizzle | `drizzle-team/drizzle-orm` | orm |
| 51 | typeorm | `typeorm/typeorm` | orm |
| 52 | sequelize | `sequelize/sequelize` | orm |
| 53 | knex | `knex/knex` | database |
| 54 | kysely | `kysely-org/kysely` | database |
| 55 | mikro-orm | `mikro-orm/mikro-orm` | orm |
| 56 | mongoose | `Automattic/mongoose` | orm |
| 57 | ioredis | `redis/ioredis` | database |
| 58 | bullmq | `taskforcesh/bullmq` | utility |
| 59 | winston | `winstonjs/winston` | logging |
| 60 | pino | `pinojs/pino` | logging |
| 61 | dotenv | `motdotla/dotenv` | config |
| 62 | jest | `jestjs/jest` | testing |
| 63 | vitest | `vitest-dev/vitest` | testing |
| 64 | chai | `chaijs/chai` | testing |
| 65 | cypress | `cypress-io/cypress` | testing |
| 66 | testing-library | `testing-library/react-testing-library` | testing |
| 67 | msw | `mswjs/msw` | testing |
| 68 | supertest | `ladjs/supertest` | testing |
| 69 | storybook | `storybookjs/storybook` | devtools |
| 70 | webpack | `webpack/webpack` | bundler |
| 71 | vite | `vitejs/vite` | bundler |
| 72 | esbuild | `evanw/esbuild` | bundler |
| 73 | rollup | `rollup/rollup` | bundler |
| 74 | parcel | `parcel-bundler/parcel` | bundler |
| 75 | turbopack | `vercel/turbo` | bundler |
| 76 | swc | `swc-project/swc` | compiler |
| 77 | babel | `babel/babel` | compiler |
| 78 | tsup | `egoist/tsup` | bundler |
| 79 | unbuild | `unjs/unbuild` | bundler |
| 80 | tsx | `privatenumber/tsx` | runtime |
| 81 | ts-node | `TypeStrong/ts-node` | runtime |
| 82 | typescript | `microsoft/TypeScript` | type |
| 83 | eslint | `eslint/eslint` | linter |
| 84 | prettier | `prettier/prettier` | formatter |
| 85 | biome | `biomejs/biome` | linter |
| 86 | oxlint | `oxc-project/oxc` | linter |
| 87 | stylelint | `stylelint/stylelint` | linter |
| 88 | tailwindcss | `tailwindlabs/tailwindcss` | css |
| 89 | unocss | `unocss/unocss` | css |
| 90 | postcss | `postcss/postcss` | css |
| 91 | sass | `sass/dart-sass` | css |
| 92 | styled-components | `styled-components/styled-components` | css |
| 93 | emotion | `emotion-js/emotion` | css |
| 94 | vanilla-extract | `vanilla-extract-css/vanilla-extract` | css |
| 95 | panda-css | `chakra-ui/panda` | css |
| 96 | radix-ui | `radix-ui/primitives` | component |
| 97 | shadcn-ui | `shadcn-ui/ui` | component |
| 98 | headless-ui | `tailwindlabs/headlessui` | component |
| 99 | ariakit | `ariakit/ariakit` | component |
| 100 | react-aria | `adobe/react-spectrum` | component |
| 101 | mantine | `mantinedev/mantine` | component |
| 102 | ant-design | `ant-design/ant-design` | component |
| 103 | material-ui | `mui/material-ui` | component |
| 104 | chakra-ui | `chakra-ui/chakra-ui` | component |
| 105 | nextui | `nextui-org/nextui` | component |
| 106 | bootstrap | `twbs/bootstrap` | css |
| 107 | framer-motion | `framer/motion` | animation |
| 108 | react-spring | `pmndrs/react-spring` | animation |
| 109 | gsap | `greensock/GSAP` | animation |
| 110 | lottie-web | `airbnb/lottie-web` | animation |
| 111 | three.js | `mrdoob/three.js` | visualization |
| 112 | react-three-fiber | `pmndrs/react-three-fiber` | visualization |
| 113 | d3 | `d3/d3` | visualization |
| 114 | chart.js | `chartjs/Chart.js` | chart |
| 115 | echarts | `apache/echarts` | chart |
| 116 | recharts | `recharts/recharts` | chart |
| 117 | nivo | `plouc/nivo` | chart |
| 118 | visx | `airbnb/visx` | chart |
| 119 | apexcharts | `apexcharts/apexcharts.js` | chart |
| 120 | mapbox-gl | `mapbox/mapbox-gl-js` | map |
| 121 | leaflet | `Leaflet/Leaflet` | map |
| 122 | deck.gl | `visgl/deck.gl` | map |
| 123 | redux | `reduxjs/redux` | state-management |
| 124 | zustand | `pmndrs/zustand` | state-management |
| 125 | jotai | `pmndrs/jotai` | state-management |
| 126 | valtio | `pmndrs/valtio` | state-management |
| 127 | mobx | `mobxjs/mobx` | state-management |
| 128 | pinia | `vuejs/pinia` | state-management |
| 129 | xstate | `statelyai/xstate` | state-management |
| 130 | tanstack-query | `TanStack/query` | state-management |
| 131 | swr | `vercel/swr` | http-client |
| 132 | apollo-client | `apollographql/apollo-client` | graphql |
| 133 | urql | `urql-graphql/urql` | graphql |
| 134 | relay | `facebook/relay` | graphql |
| 135 | graphql-js | `graphql/graphql-js` | graphql |
| 136 | type-graphql | `MichalLyworski/type-graphql` | graphql |
| 137 | pothos | `hayes/pothos` | graphql |
| 138 | graphql-yoga | `dotansimha/graphql-yoga` | graphql |
| 139 | socket.io | `socketio/socket.io` | websocket |
| 140 | ws | `websockets/ws` | websocket |
| 141 | mqtt.js | `mqttjs/MQTT.js` | realtime |
| 142 | supabase-js | `supabase/supabase-js` | database |
| 143 | firebase | `firebase/firebase-js-sdk` | database |
| 144 | aws-amplify | `aws-amplify/amplify-js` | framework |
| 145 | clerk | `clerk/javascript` | auth |
| 146 | lucia | `lucia-auth/lucia` | auth |
| 147 | next-auth | `nextauthjs/next-auth` | auth |
| 148 | passport | `jaredhanson/passport` | auth |
| 149 | jsonwebtoken | `auth0/node-jsonwebtoken` | auth |
| 150 | bcrypt | `kelektiv/node.bcrypt.js` | crypto |
| 151 | nanoid | `ai/nanoid` | utility |
| 152 | uuid | `uuidjs/uuid` | utility |
| 153 | react-hook-form | `react-hook-form/react-hook-form` | form |
| 154 | formik | `jaredpalmer/formik` | form |
| 155 | react-select | `JedWatson/react-select` | component |
| 156 | tanstack-table | `TanStack/table` | component |
| 157 | tanstack-virtual | `TanStack/virtual` | component |
| 158 | react-router | `remix-run/react-router` | routing |
| 159 | next-intl | `amannn/next-intl` | utility |
| 160 | i18next | `i18next/i18next` | utility |
| 161 | sharp | `lovell/sharp` | media |
| 162 | pdfkit | `foliojs/pdfkit` | pdf |
| 163 | jspdf | `parallax/jsPDF` | pdf |
| 164 | pdf-lib | `Hopding/pdf-lib` | pdf |
| 165 | exceljs | `exceljs/exceljs` | file |
| 166 | sheetjs | `SheetJS/sheetjs` | file |
| 167 | papaparse | `mholt/PapaParse` | file |
| 168 | nodemailer | `nodemailer/nodemailer` | email |
| 169 | react-email | `resend/react-email` | email |
| 170 | stripe | `stripe/stripe-node` | payment |
| 171 | openai | `openai/openai-node` | ai |
| 172 | anthropic-sdk | `anthropics/anthropic-sdk-typescript` | ai |
| 173 | langchain | `langchain-ai/langchainjs` | ai |
| 174 | vercel-ai | `vercel/ai` | ai |
| 175 | tensorflow.js | `tensorflow/tfjs` | ml |
| 176 | commander | `tj/commander.js` | cli |
| 177 | yargs | `yargs/yargs` | cli |
| 178 | inquirer | `SBoudrias/Inquirer.js` | cli |
| 179 | prompts | `terkelg/prompts` | cli |
| 180 | clack | `natemoo-re/clack` | cli |
| 181 | chalk | `chalk/chalk` | cli |
| 182 | picocolors | `alexeyraspopov/picocolors` | cli |
| 183 | ora | `sindresorhus/ora` | cli |
| 184 | ink | `vadimdemedes/ink` | cli |
| 185 | execa | `sindresorhus/execa` | cli |
| 186 | zx | `google/zx` | cli |
| 187 | glob | `isaacs/node-glob` | file |
| 188 | fast-glob | `mrmlnc/fast-glob` | file |
| 189 | chokidar | `paulmillr/chokidar` | file |
| 190 | fs-extra | `jprichardson/node-fs-extra` | file |
| 191 | lerna | `lerna/lerna` | monorepo |
| 192 | nx | `nrwl/nx` | monorepo |
| 193 | turborepo | `vercel/turbo` | monorepo |
| 194 | changesets | `changesets/changesets` | monorepo |
| 195 | semantic-release | `semantic-release/semantic-release` | devtools |
| 196 | electron | `electron/electron` | desktop |
| 197 | tauri | `tauri-apps/tauri` | desktop |
| 198 | react-native | `facebook/react-native` | mobile |
| 199 | expo | `expo/expo` | mobile |
| 200 | capacitor | `ionic-team/capacitor` | mobile |
| 201 | mocha | `mochajs/mocha` | testing |
| 202 | sinon | `sinonjs/sinon` | testing |
| 203 | ava | `avajs/ava` | testing |
| 204 | tape | `ljharb/tape` | testing |
| 205 | node-tap | `tapjs/node-tap` | testing |
| 206 | uvu | `lukeed/uvu` | testing |
| 207 | happy-dom | `capricorn86/happy-dom` | testing |
| 208 | jsdom | `jsdom/jsdom` | testing |
| 209 | linkedom | `WebReflection/linkedom` | testing |
| 210 | nock | `nock/nock` | testing |
| 211 | miragejs | `miragejs/miragejs` | testing |
| 212 | json-server | `typicode/json-server` | devtools |
| 213 | concurrently | `open-cli-tools/concurrently` | devtools |
| 214 | npm-run-all | `mysticatea/npm-run-all` | devtools |
| 215 | cross-env | `kentcdodds/cross-env` | devtools |
| 216 | rimraf | `isaacs/rimraf` | file |
| 217 | mkdirp | `isaacs/node-mkdirp` | file |
| 218 | shelljs | `shelljs/shelljs` | cli |
| 219 | listr2 | `listr2/listr2` | cli |
| 220 | consola | `unjs/consola` | logging |
| 221 | defu | `unjs/defu` | utility |
| 222 | ofetch | `unjs/ofetch` | http-client |
| 223 | ufo | `unjs/ufo` | utility |
| 224 | pathe | `unjs/pathe` | utility |
| 225 | destr | `unjs/destr` | utility |
| 226 | changelogen | `unjs/changelogen` | devtools |
| 227 | pkg | `vercel/pkg` | bundler |
| 228 | ncc | `vercel/ncc` | bundler |
| 229 | nexe | `nexe/nexe` | bundler |
| 230 | boxen | `sindresorhus/boxen` | cli |
| 231 | figures | `sindresorhus/figures` | cli |
| 232 | gradient-string | `bokub/gradient-string` | cli |
| 233 | terminal-link | `sindresorhus/terminal-link` | cli |
| 234 | update-notifier | `yeoman/update-notifier` | cli |
| 235 | meow | `sindresorhus/meow` | cli |
| 236 | cac | `cacjs/cac` | cli |
| 237 | mri | `lukeed/mri` | cli |
| 238 | arg | `vercel/arg` | cli |
| 239 | minimist | `minimistjs/minimist` | cli |
| 240 | cosmiconfig | `cosmiconfig/cosmiconfig` | config |
| 241 | c12 | `unjs/c12` | config |
| 242 | unconfig | `antfu/unconfig` | config |
| 243 | giget | `unjs/giget` | devtools |
| 244 | degit | `Rich-Harris/degit` | devtools |
| 245 | create-t3-app | `t3-oss/create-t3-app` | scaffold |
| 246 | yeoman | `yeoman/yo` | scaffold |
| 247 | plop | `plopjs/plop` | scaffold |
| 248 | hygen | `jondot/hygen` | scaffold |
| 249 | projen | `projen/projen` | scaffold |
| 250 | cookie | `jshttp/cookie` | server |
| 251 | tough-cookie | `salesforce/tough-cookie` | http-client |
| 252 | express-session | `expressjs/session` | server |
| 253 | cors | `expressjs/cors` | server |
| 254 | helmet | `helmetjs/helmet` | server |
| 255 | express-rate-limit | `express-rate-limit/express-rate-limit` | server |
| 256 | express-validator | `express-validator/express-validator` | validation |
| 257 | multer | `expressjs/multer` | server |
| 258 | formidable | `node-formidable/formidable` | server |
| 259 | busboy | `mscdex/busboy` | server |
| 260 | body-parser | `expressjs/body-parser` | server |
| 261 | compression | `expressjs/compression` | server |
| 262 | serve-static | `expressjs/serve-static` | server |
| 263 | morgan | `expressjs/morgan` | logging |
| 264 | http-proxy-middleware | `chimurai/http-proxy-middleware` | server |
| 265 | proxy-agent | `TooTallNate/proxy-agents` | http-client |
| 266 | https-proxy-agent | `TooTallNate/proxy-agents` | http-client |
| 267 | agentkeepalive | `node-modules/agentkeepalive` | http-client |
| 268 | p-retry | `sindresorhus/p-retry` | utility |
| 269 | p-limit | `sindresorhus/p-limit` | utility |
| 270 | p-queue | `sindresorhus/p-queue` | utility |
| 271 | p-map | `sindresorhus/p-map` | utility |
| 272 | p-throttle | `sindresorhus/p-throttle` | utility |
| 273 | bottleneck | `SGrondin/bottleneck` | utility |
| 274 | rate-limiter-flexible | `animir/node-rate-limiter-flexible` | utility |
| 275 | keyv | `jaredwray/keyv` | database |
| 276 | lru-cache | `isaacs/node-lru-cache` | utility |
| 277 | quick-lru | `sindresorhus/quick-lru` | utility |
| 278 | node-cache | `node-cache/node-cache` | utility |
| 279 | unstorage | `unjs/unstorage` | database |
| 280 | upstash-redis | `upstash/upstash-redis` | database |
| 281 | nitropack | `unjs/nitro` | server |
| 282 | vinxi | `nksaraf/vinxi` | meta-framework |
| 283 | tanstack-router | `TanStack/router` | routing |
| 284 | tanstack-form | `TanStack/form` | form |
| 285 | tanstack-start | `TanStack/start` | meta-framework |
| 286 | wouter | `molefrog/wouter` | routing |
| 287 | path-to-regexp | `pillarjs/path-to-regexp` | routing |
| 288 | cron | `kelektiv/node-cron` | utility |
| 289 | node-schedule | `node-schedule/node-schedule` | utility |
| 290 | bree | `breejs/bree` | utility |
| 291 | croner | `Hexagon/croner` | utility |
| 292 | octokit | `octokit/octokit.js` | api |
| 293 | simple-git | `steveukx/git-js` | devtools |
| 294 | isomorphic-git | `isomorphic-git/isomorphic-git` | devtools |
| 295 | docusaurus | `facebook/docusaurus` | meta-framework |
| 296 | nextra | `shuding/nextra` | meta-framework |
| 297 | vuepress | `vuejs/vuepress` | meta-framework |
| 298 | mdx | `mdx-js/mdx` | markdown |
| 299 | remark | `remarkjs/remark` | markdown |
| 300 | rehype | `rehypejs/rehype` | markdown |
| 301 | unified | `unifiedjs/unified` | markdown |
| 302 | shiki | `shikijs/shiki` | syntax-highlight |
| 303 | prismjs | `PrismJS/prism` | syntax-highlight |
| 304 | highlight.js | `highlightjs/highlight.js` | syntax-highlight |
| 305 | monaco-editor | `microsoft/monaco-editor` | editor |
| 306 | codemirror | `codemirror/dev` | editor |
| 307 | tiptap | `ueberdosis/tiptap` | editor |
| 308 | lexical | `facebook/lexical` | editor |
| 309 | quill | `slab/quill` | editor |
| 310 | slate | `ianstormtaylor/slate` | editor |
| 311 | prosemirror | `ProseMirror/prosemirror` | editor |
| 312 | draft-js | `facebookarchive/draft-js` | editor |
| 313 | editor-js | `codex-team/editor.js` | editor |
| 314 | milkdown | `Milkdown/milkdown` | editor |
| 315 | blocknote | `TypeCellOS/BlockNote` | editor |
| 316 | novel | `steven-tey/novel` | editor |
| 317 | plate | `udecode/plate` | editor |
| 318 | sanity | `sanity-io/sanity` | cms |
| 319 | strapi | `strapi/strapi` | cms |
| 320 | payload | `payloadcms/payload` | cms |
| 321 | directus | `directus/directus` | cms |
| 322 | ghost | `TryGhost/Ghost` | cms |
| 323 | keystone | `keystonejs/keystone` | cms |
| 324 | medusa | `medusajs/medusa` | ecommerce |
| 325 | vendure | `vendure-ecommerce/vendure` | ecommerce |
| 326 | saleor | `saleor/saleor-storefront` | ecommerce |
| 327 | shopify-api | `Shopify/shopify-api-js` | ecommerce |
| 328 | contentlayer | `contentlayerdev/contentlayer` | cms |
| 329 | fumadocs | `fuma-nama/fumadocs` | meta-framework |
| 330 | keystatic | `Thinkmill/keystatic` | cms |
| 331 | marked | `markedjs/marked` | markdown |
| 332 | markdown-it | `markdown-it/markdown-it` | markdown |
| 333 | turndown | `mixmark-io/turndown` | markdown |
| 334 | dompurify | `cure53/DOMPurify` | security |
| 335 | sanitize-html | `apostrophecms/sanitize-html` | security |
| 336 | helmet-csp | `helmetjs/csp` | security |
| 337 | class-validator | `typestack/class-validator` | validation |
| 338 | class-transformer | `typestack/class-transformer` | utility |
| 339 | reflect-metadata | `rbuckton/reflect-metadata` | utility |
| 340 | tsyringe | `microsoft/tsyringe` | utility |
| 341 | inversify | `inversify/InversifyJS` | utility |
| 342 | awilix | `jeffijoe/awilix` | utility |
| 343 | typedi | `typestack/typedi` | utility |
| 344 | rxjs | `ReactiveX/rxjs` | utility |
| 345 | immer | `immerjs/immer` | utility |
| 346 | immutable | `immutable-js/immutable-js` | utility |
| 347 | superjson | `blitz-js/superjson` | utility |
| 348 | devalue | `Rich-Harris/devalue` | utility |
| 349 | qs | `ljharb/qs` | utility |
| 350 | query-string | `sindresorhus/query-string` | utility |
| 351 | eventemitter3 | `primus/eventemitter3` | utility |
| 352 | mitt | `developit/mitt` | utility |
| 353 | on-change | `sindresorhus/on-change` | utility |
| 354 | type-fest | `sindresorhus/type-fest` | type |
| 355 | ts-pattern | `gvergnaud/ts-pattern` | type |
| 356 | ts-morph | `dsherret/ts-morph` | type |
| 357 | ts-toolbelt | `millsp/ts-toolbelt` | type |
| 358 | zx-cpy | `sindresorhus/cpy` | file |
| 359 | del | `sindresorhus/del` | file |
| 360 | globby | `sindresorhus/globby` | file |
| 361 | tempy | `sindresorhus/tempy` | file |
| 362 | env-cmd | `toddbluhm/env-cmd` | config |
| 363 | envalid | `af/envalid` | config |
| 364 | convict | `mozilla/node-convict` | config |
| 365 | rc | `dominictarr/rc` | config |
| 366 | conf | `sindresorhus/conf` | config |
| 367 | nconf | `indexzero/nconf` | config |
| 368 | husky | `typicode/husky` | devtools |
| 369 | lint-staged | `lint-staged/lint-staged` | devtools |
| 370 | commitlint | `conventional-changelog/commitlint` | devtools |
| 371 | standard-version | `conventional-changelog/standard-version` | devtools |
| 372 | release-it | `release-it/release-it` | devtools |
| 373 | auto-changelog | `cookpete/auto-changelog` | devtools |
| 374 | size-limit | `ai/size-limit` | devtools |
| 375 | bundlewatch | `bundlewatch/bundlewatch` | devtools |
| 376 | madge | `pahen/madge` | devtools |
| 377 | depcheck | `depcheck/depcheck` | devtools |
| 378 | knip | `webpro/knip` | devtools |
| 379 | socket.io-client | `socketio/socket.io-client` | websocket |
| 380 | engine.io | `socketio/engine.io` | websocket |
| 381 | faye-websocket | `faye/faye-websocket-node` | websocket |
| 382 | peerjs | `peers/peerjs` | realtime |
| 383 | y-js | `yjs/yjs` | realtime |
| 384 | automerge | `automerge/automerge` | realtime |
| 385 | liveblocks | `liveblocks/liveblocks` | realtime |
| 386 | partykit | `partykit/partykit` | realtime |
| 387 | onnxruntime-web | `microsoft/onnxruntime` | ml |
| 388 | transformers-js | `xenova/transformers.js` | ml |
| 389 | brain.js | `BrainJS/brain.js` | ml |
| 390 | ml5 | `ml5js/ml5-library` | ml |
| 391 | nsfwjs | `infinitered/nsfwjs` | ml |
| 392 | jimp | `jimp-dev/jimp` | media |
| 393 | pica | `nodeca/pica` | media |
| 394 | blurhash | `woltapp/blurhash` | media |
| 395 | sqip | `axe312ger/sqip` | media |
| 396 | ffmpeg-wasm | `ffmpegwasm/ffmpeg.wasm` | media |
| 397 | howler | `goldfire/howler.js` | media |
| 398 | tone | `Tonejs/Tone.js` | media |
| 399 | wavesurfer | `katspaugh/wavesurfer.js` | media |
| 400 | video-js | `videojs/video.js` | media |
| 401 | canvas | `Automattic/node-canvas` | image-processing |
| 402 | image-size | `image-size/image-size` | image-processing |
| 403 | probe-image-size | `nodeca/probe-image-size` | image-processing |
| 404 | thumbhash | `evanw/thumbhash` | image-processing |
| 405 | plaiceholder | `joe-bell/plaiceholder` | image-processing |
| 406 | cloudinary | `cloudinary/cloudinary_npm` | image-processing |
| 407 | cropperjs | `fengyuanchen/cropperjs` | image-processing |
| 408 | fluent-ffmpeg | `fluent-ffmpeg/node-fluent-ffmpeg` | video-audio |
| 409 | hls.js | `video-dev/hls.js` | video-audio |
| 410 | video.js | `videojs/video.js` | video-audio |
| 411 | plyr | `sampotts/plyr` | video-audio |
| 412 | shaka-player | `shaka-project/shaka-player` | video-audio |
| 413 | dash.js | `Dash-Industry-Forum/dash.js` | video-audio |
| 414 | mediasoup | `versatica/mediasoup` | video-audio |
| 415 | livekit | `livekit/client-sdk-js` | video-audio |
| 416 | tone.js | `Tonejs/Tone.js` | video-audio |
| 417 | howler.js | `goldfire/howler.js` | video-audio |
| 418 | wavesurfer.js | `katspaugh/wavesurfer.js` | video-audio |
| 419 | peaks.js | `bbc/peaks.js` | video-audio |
| 420 | babylon.js | `BabylonJS/Babylon.js` | 3d-webgl |
| 421 | aframe | `aframevr/aframe` | 3d-webgl |
| 422 | playcanvas | `playcanvas/engine` | 3d-webgl |
| 423 | ogl | `oframe/ogl` | 3d-webgl |
| 424 | regl | `regl-project/regl` | 3d-webgl |
| 425 | gpu.js | `gpujs/gpu.js` | 3d-webgl |
| 426 | model-viewer | `google/model-viewer` | 3d-webgl |
| 427 | turf | `Turfjs/turf` | maps-geo |
| 428 | maplibre-gl | `maplibre/maplibre-gl-js` | maps-geo |
| 429 | openlayers | `openlayers/openlayers` | maps-geo |
| 430 | cesium | `CesiumGS/cesium` | maps-geo |
| 431 | h3-js | `uber/h3-js` | maps-geo |
| 432 | supercluster | `mapbox/supercluster` | maps-geo |
| 433 | rbush | `mourner/rbush` | maps-geo |
| 434 | proj4 | `proj4js/proj4js` | maps-geo |
| 435 | geolib | `manuelbieh/geolib` | maps-geo |
| 436 | anime.js | `juliangarnier/anime` | animation |
| 437 | popmotion | `Popmotion/popmotion` | animation |
| 438 | motion-one | `motiondivision/motionone` | animation |
| 439 | auto-animate | `formkit/auto-animate` | animation |
| 440 | paper.js | `paperjs/paper.js` | animation |
| 441 | two.js | `jonobr1/two.js` | animation |
| 442 | p5 | `processing/p5.js` | creative-coding |
| 443 | konva | `konvajs/konva` | canvas |
| 444 | fabric.js | `fabricjs/fabric.js` | canvas |
| 445 | pixijs | `pixijs/pixijs` | canvas |
| 446 | phaser | `phaserjs/phaser` | game-engine |
| 447 | matter-js | `liabru/matter-js` | physics |
| 448 | cannon-es | `pmndrs/cannon-es` | physics |
| 449 | rapier-js | `dimforge/rapier.js` | physics |
| 450 | react-pdf | `diegomura/react-pdf` | pdf-document |
| 451 | pdf-parse | `modesty/pdf-parse` | pdf-document |
| 452 | docxtemplater | `open-xml-templating/docxtemplater` | pdf-document |
| 453 | mammoth | `mwilliamson/mammoth.js` | pdf-document |
| 454 | showdown | `showdownjs/showdown` | pdf-document |
| 455 | micromark | `micromark/micromark` | markdown |
| 456 | gray-matter | `jonschlinkert/gray-matter` | markdown |
| 457 | yaml | `eemeli/yaml` | serialization |
| 458 | json5 | `json5/json5` | serialization |
| 459 | serialize-javascript | `yahoo/serialize-javascript` | serialization |
| 460 | mjml | `mjmlio/mjml` | email |
| 461 | mailing | `sofn-xyz/mailing` | email |
| 462 | sendgrid-js | `sendgrid/sendgrid-nodejs` | email |
| 463 | postmark | `ActiveCampaign/postmark.js` | email |
| 464 | oslo | `pilcrowOnPaper/oslo` | auth |
| 465 | arctic | `pilcrowOnPaper/arctic` | auth |
| 466 | better-auth | `better-auth/better-auth` | auth |
| 467 | iron-session | `vvo/iron-session` | auth |
| 468 | keycloak-js | `keycloak/keycloak` | auth |
| 469 | auth0-js | `auth0/auth0.js` | auth |
| 470 | magic-sdk | `magiclabs/magic-js` | auth |
| 471 | ethers | `ethers-io/ethers.js` | web3 |
| 472 | web3.js | `web3/web3.js` | web3 |
| 473 | viem | `wagmi-dev/viem` | web3 |
| 474 | wagmi | `wagmi-dev/wagmi` | web3 |
| 475 | rainbowkit | `rainbow-me/rainbowkit` | web3 |
| 476 | thirdweb | `thirdweb-dev/js` | web3 |
| 477 | moralis | `MoralisWeb3/Moralis-JS-SDK` | web3 |
| 478 | lemonsqueezy | `lmsqueezy/lemonsqueezy.js` | payment |
| 479 | paddle-js | `PaddleHQ/paddle-node-sdk` | payment |
| 480 | paypal-js | `paypal/paypal-js` | payment |
| 481 | braintree | `braintree/braintree_node` | payment |
| 482 | ably | `ably/ably-js` | realtime |
| 483 | pusher-js | `pusher/pusher-js` | realtime |
| 484 | yjs | `yjs/yjs` | realtime |
| 485 | gun | `amark/gun` | realtime |
| 486 | simple-peer | `feross/simple-peer` | realtime |
| 487 | libp2p | `libp2p/js-libp2p` | realtime |
| 488 | sst | `sst/sst` | serverless |
| 489 | serverless-framework | `serverless/serverless` | serverless |
| 490 | middy | `middyjs/middy` | serverless |
| 491 | powertools-lambda-ts | `aws-powertools/powertools-lambda-typescript` | serverless |
| 492 | nightwatch | `nightwatchjs/nightwatch` | testing |
| 493 | webdriverio | `webdriverio/webdriverio` | testing |
| 494 | detox | `wix/Detox` | testing |
| 495 | testcafe | `DevExpress/testcafe` | testing |
| 496 | pactjs | `pact-foundation/pact-js` | testing |
| 497 | codeceptjs | `codeceptjs/CodeceptJS` | testing |
| 498 | lingui | `lingui/js-lingui` | i18n |
| 499 | typesafe-i18n | `ivanhofer/typesafe-i18n` | i18n |
| 500 | paraglide | `opral/monorepo` | i18n |
| 501 | messageformat | `messageformat/messageformat` | i18n |
| 502 | rosetta | `lukeed/rosetta` | i18n |
| 503 | axe-core | `dequelabs/axe-core` | accessibility |
| 504 | pa11y | `pa11y/pa11y` | accessibility |
| 505 | lighthouse | `GoogleChrome/lighthouse` | accessibility |
| 506 | unlighthouse | `harlan-zw/unlighthouse` | accessibility |
| 507 | jsx-a11y | `jsx-eslint/eslint-plugin-jsx-a11y` | accessibility |
| 508 | next-seo | `garmeeh/next-seo` | seo |
| 509 | next-sitemap | `iamvishnusankar/next-sitemap` | seo |
| 510 | schema-dts | `google/schema-dts` | seo |
| 511 | sentry-js | `getsentry/sentry-javascript` | monitoring |
| 512 | logrocket | `LogRocket/logrocket` | monitoring |
| 513 | posthog-js | `PostHog/posthog-js` | monitoring |
| 514 | mixpanel | `mixpanel/mixpanel-js` | monitoring |
| 515 | amplitude | `amplitude/Amplitude-TypeScript` | monitoring |
| 516 | segment | `segmentio/analytics-next` | monitoring |
| 517 | plausible-tracker | `plausible/plausible-tracker` | monitoring |
| 518 | fathom-client | `derrickreimer/fathom-client` | monitoring |
| 519 | unleash-proxy | `Unleash/unleash-client-node` | feature-flags |
| 520 | flagsmith | `Flagsmith/flagsmith-js-client` | feature-flags |
| 521 | launchdarkly | `launchdarkly/js-core` | feature-flags |
| 522 | growthbook | `growthbook/growthbook` | feature-flags |
| 523 | openfeature | `open-feature/js-sdk` | feature-flags |
| 524 | transformers.js | `xenova/transformers.js` | ml |
| 525 | face-api.js | `justadudewhohacks/face-api.js` | ml |
| 526 | dnd-kit | `clauderic/dnd-kit` | component |
| 527 | react-beautiful-dnd | `atlassian/react-beautiful-dnd` | component |
| 528 | react-dropzone | `react-dropzone/react-dropzone` | component |
| 529 | react-window | `bvaughn/react-window` | component |
| 530 | react-virtuoso | `petyosi/react-virtuoso` | component |
| 531 | swiper | `nolimits4web/swiper` | component |
| 532 | embla-carousel | `davidjerleke/embla-carousel` | component |
| 533 | react-toastify | `fkhadra/react-toastify` | component |
| 534 | sonner | `emilkowalski/sonner` | component |
| 535 | cmdk | `pacocoursey/cmdk` | component |
| 536 | vaul | `emilkowalski/vaul` | component |
| 537 | react-hot-toast | `timolins/react-hot-toast` | component |
| 538 | neverthrow | `supermacro/neverthrow` | utility |
| 539 | ts-reset | `total-typescript/ts-reset` | utility |
| 540 | ulid | `ulid/javascript` | utility |
| 541 | faker-js | `faker-js/faker` | testing |
| 542 | chancejs | `chancejs/chancejs` | testing |
| 543 | polka | `lukeed/polka` | server |
| 544 | sirv | `lukeed/sirv` | server |
| 545 | agenda | `agenda/agenda` | scheduling |
| 546 | archiver | `archiverjs/node-archiver` | file |
| 547 | adm-zip | `cthackers/adm-zip` | file |
| 548 | tar | `isaacs/node-tar` | file |
| 549 | tmp | `raszi/node-tmp` | file |
| 550 | mime-types | `jshttp/mime-types` | file |
| 551 | file-type | `sindresorhus/file-type` | file |
| 552 | tus-js-client | `tus/tus-js-client` | file-upload |
| 553 | uppy | `transloadit/uppy` | file-upload |
| 554 | filepond | `pqina/filepond` | file-upload |
| 555 | tinypool | `tinylibs/tinypool` | concurrency |
| 556 | workerpool | `josdejong/workerpool` | concurrency |
| 557 | piscina | `piscinajs/piscina` | concurrency |
| 558 | comlink | `GoogleChromeLabs/comlink` | concurrency |
| 559 | redux-devtools | `reduxjs/redux-devtools` | devtools |
| 560 | why-did-you-render | `welldone-software/why-did-you-render` | devtools |
| 561 | react-scan | `aidenybai/react-scan` | devtools |
| 562 | million | `aidenybai/million` | performance |
| 563 | partytown | `BuilderIO/partytown` | performance |
| 564 | quicklink | `GoogleChromeLabs/quicklink` | performance |
| 565 | idb | `jakearchibald/idb` | storage |
| 566 | dexie | `dexie/Dexie.js` | storage |
| 567 | localforage | `localForage/localForage` | storage |
| 568 | sql.js | `sql-js/sql.js` | database |
| 569 | better-sqlite3 | `WiseLibs/better-sqlite3` | database |
| 570 | postgres | `porsager/postgres` | database |
| 571 | slonik | `gajus/slonik` | database |
| 572 | redis | `redis/node-redis` | database |
| 573 | robot | `matthewp/robot` | state-machines |
| 574 | machina | `ifandelse/machina.js` | state-machines |
| 575 | vest | `ealush/vest` | forms |
| 576 | react-final-form | `final-form/react-final-form` | forms |
| 577 | conform | `edmundhung/conform` | forms |
| 578 | superforms | `ciscoheat/sveltekit-superforms` | forms |
| 579 | remix-validated-form | `airjp73/remix-validated-form` | forms |
| 580 | ag-grid | `ag-grid/ag-grid` | tables-data-grid |
| 581 | handsontable | `handsontable/handsontable` | tables-data-grid |
| 582 | tabulator | `olifolkerd/tabulator` | tables-data-grid |
| 583 | glide-data-grid | `glideapps/glide-data-grid` | tables-data-grid |
| 584 | react-data-grid | `adazzle/react-data-grid` | tables-data-grid |
| 585 | primereact | `primefaces/primereact` | tables-data-grid |
| 586 | primevue | `primefaces/primevue` | tables-data-grid |
| 587 | primeng | `primefaces/primeng` | tables-data-grid |
| 588 | dropzone | `dropzone/dropzone` | file-upload |
| 589 | uploadthing | `pingdotgg/uploadthing` | file-upload |
| 590 | pragmatic-drag-and-drop | `atlassian/pragmatic-drag-and-drop` | drag-drop |
| 591 | sortablejs | `SortableJS/Sortable` | drag-drop |
| 592 | vuedraggable | `SortableJS/vue.draggable.next` | drag-drop |
| 593 | svelte-dnd-action | `isaacHagworthy/svelte-dnd-action` | drag-drop |
| 594 | vue-virtual-scroller | `Akryum/vue-virtual-scroller` | virtual-scroll |
| 595 | keen-slider | `rcbyr/keen-slider` | carousel |
| 596 | flicking | `naver/egjs-flicking` | carousel |
| 597 | splide | `Splidejs/splide` | carousel |
| 598 | glidejs | `glidejs/glide` | carousel |
| 599 | react-modal | `reactjs/react-modal` | modal-dialog |
| 600 | sweetalert2 | `sweetalert2/sweetalert2` | modal-dialog |
| 601 | notistack | `iamhosseindhv/notistack` | modal-dialog |
| 602 | vue-toastification | `Maronato/vue-toastification` | modal-dialog |
| 603 | tippy.js | `atomiks/tippyjs` | tooltip |
| 604 | floating-ui | `floating-ui/floating-ui` | tooltip |
| 605 | react-datepicker | `Hacker0x01/react-datepicker` | date-picker |
| 606 | flatpickr | `flatpickr/flatpickr` | date-picker |
| 607 | pikaday | `Pikaday/Pikaday` | date-picker |
| 608 | litepicker | `wakirin/Litepicker` | date-picker |
| 609 | chroma-js | `gka/chroma.js` | color |
| 610 | tinycolor2 | `bgrins/TinyColor` | color |
| 611 | culori | `Evercoder/culori` | color |
| 612 | mathjs | `josdejong/mathjs` | math |
| 613 | decimal.js | `MikeMcl/decimal.js` | math |
| 614 | big.js | `MikeMcl/big.js` | math |
| 615 | bignumber.js | `MikeMcl/bignumber.js` | math |
| 616 | fraction.js | `infusion/Fraction.js` | math |
| 617 | complex.js | `infusion/Complex.js` | math |
| 618 | crypto-js | `brix/crypto-js` | crypto |
| 619 | tweetnacl | `dchest/tweetnacl-js` | crypto |
| 620 | noble-curves | `paulmillr/noble-curves` | crypto |
| 621 | noble-hashes | `paulmillr/noble-hashes` | crypto |
| 622 | scure-base | `paulmillr/scure-base` | crypto |
| 623 | jose | `panva/jose` | crypto |
| 624 | node-forge | `digitalbazaar/forge` | crypto |
| 625 | openpgp | `openpgpjs/openpgpjs` | crypto |
| 626 | fflate | `101arrowz/fflate` | compression |
| 627 | pako | `nodeca/pako` | compression |
| 628 | lz-string | `pieroxy/lz-string` | compression |
| 629 | rxdb | `pubkey/rxdb` | storage |
| 630 | watermelondb | `Nozbe/WatermelonDB` | storage |
| 631 | pouchdb | `pouchdb/pouchdb` | storage |
| 632 | neon-serverless | `neondatabase/serverless` | storage |
| 633 | convex | `get-convex/convex-js` | storage |
| 634 | svgo | `svg/svgo` | image-optimization |
| 635 | imagemin | `imagemin/imagemin` | image-optimization |
| 636 | unpic | `ascorbic/unpic` | image-optimization |
| 637 | unplugin | `unjs/unplugin` | bundler-plugins |
| 638 | vite-plugin-pwa | `vite-pwa/vite-plugin-pwa` | bundler-plugins |
| 639 | rollup-plugin-visualizer | `btd/rollup-plugin-visualizer` | bundler-plugins |
| 640 | webpack-bundle-analyzer | `webpack-contrib/webpack-bundle-analyzer` | bundler-plugins |
| 641 | mini-css-extract-plugin | `webpack-contrib/mini-css-extract-plugin` | bundler-plugins |
| 642 | terser-webpack-plugin | `webpack-contrib/terser-webpack-plugin` | bundler-plugins |
| 643 | html-webpack-plugin | `jantimon/html-webpack-plugin` | bundler-plugins |
| 644 | node-gyp | `nodejs/node-gyp` | node-native |
| 645 | node-addon-api | `nodejs/node-addon-api` | node-native |
| 646 | napi-rs | `napi-rs/napi-rs` | node-native |
| 647 | xterm.js | `xtermjs/xterm.js` | cli-frameworks |
| 648 | node-pty | `microsoft/node-pty` | cli-frameworks |
| 649 | blessed | `chjj/blessed` | cli-frameworks |
| 650 | blessed-contrib | `yaronn/blessed-contrib` | cli-frameworks |
| 651 | terminal-kit | `cronvel/terminal-kit` | cli-frameworks |
| 652 | gluegun | `infinitered/gluegun` | cli-frameworks |
| 653 | pastel | `vadimdemedes/pastel` | cli-frameworks |
| 654 | caporal | `mattallty/Caporal.js` | cli-frameworks |
| 655 | http-proxy | `http-party/node-http-proxy` | networking |
| 656 | trigger-dev | `triggerdotdev/trigger.dev` | scheduling |
| 657 | inngest | `inngest/inngest-js` | scheduling |
| 658 | n8n | `n8n-io/n8n` | workflow |
| 659 | activepieces | `activepieces/activepieces` | workflow |
| 660 | windmill-client | `windmill-labs/windmill` | workflow |
| 661 | contentful | `contentful/contentful.js` | headless-cms |
| 662 | storyblok | `storyblok/storyblok-js-client` | headless-cms |
| 663 | prismic | `prismicio/prismic-client` | headless-cms |
| 664 | builder-io | `BuilderIO/builder` | headless-cms |
| 665 | sanity-client | `sanity-io/client` | headless-cms |
| 666 | tina | `tinacms/tinacms` | headless-cms |
| 667 | decap-cms | `decaporg/decap-cms` | headless-cms |
| 668 | outstatic | `avitorio/outstatic` | headless-cms |
| 669 | kontent-ai | `kontent-ai/delivery-sdk-js` | headless-cms |
| 670 | meilisearch-js | `meilisearch/meilisearch-js` | search |
| 671 | typesense-js | `typesense/typesense-js` | search |
| 672 | orama | `oramasearch/orama` | search |
| 673 | flexsearch | `nextapps-de/flexsearch` | search |
| 674 | fuse.js | `krisk/Fuse` | search |
| 675 | lunr | `olivernn/lunr.js` | search |
| 676 | minisearch | `lucaong/minisearch` | search |
| 677 | pagefind | `CloudCannon/pagefind` | search |
| 678 | neutralino | `nicolo-ribaudo/neutralinojs` | desktop |
| 679 | nativewind | `marklawlor/nativewind` | mobile |
| 680 | tamagui | `tamagui/tamagui` | mobile |
| 681 | solito | `nandorojo/solito` | mobile |
| 682 | react-native-web | `nicolo-ribaudo/react-native-web` | mobile |
| 683 | restyle | `Shopify/restyle` | mobile |
| 684 | dripsy | `nandorojo/dripsy` | mobile |
| 685 | unistyles | `jpudysz/react-native-unistyles` | mobile |
| 686 | snipcart | `snipcart/snipcart-theme-v2` | e-commerce |
| 687 | swell-js | `swellstores/swell-js` | e-commerce |
| 688 | react-virtualized | `bvaughn/react-virtualized` | virtual-scroll |
| 689 | clsx | `lukeed/clsx` | utility |
| 690 | classnames | `JedWatson/classnames` | utility |
| 691 | deepmerge | `TehShrike/deepmerge` | utility |
| 692 | wretch | `elbywan/wretch` | http-client |
| 693 | redaxios | `developit/redaxios` | http-client |
| 694 | superstruct | `ianstormtaylor/superstruct` | validation |
| 695 | ow | `sindresorhus/ow` | validation |
| 696 | tsconfig-paths | `dividab/tsconfig-paths` | typescript-utility |
| 697 | elysia | `elysiajs/elysia` | server-framework |
| 698 | restify | `restify/node-restify` | server-framework |
| 699 | micro | `vercel/micro` | server-framework |
| 700 | autocannon | `mcollina/autocannon` | testing-benchmarking |
| 701 | clinic | `clinicjs/node-clinic` | testing-benchmarking |
| 702 | 0x | `davidmarkclements/0x` | testing-benchmarking |
| 703 | testcontainers-node | `testcontainers/testcontainers-node` | testing |
| 704 | citty | `unjs/citty` | cli-utility |
| 705 | cleye | `privatenumber/cleye` | cli-utility |
| 706 | radash | `sodiray/radash` | utility |
| 707 | es-toolkit | `toss/es-toolkit` | utility |
| 708 | remeda | `remeda/remeda` | utility |
| 709 | cva | `joe-bell/cva` | styling |
| 710 | tailwind-merge | `dcastil/tailwind-merge` | styling |
| 711 | tailwind-variants | `nextui-org/tailwind-variants` | styling |
| 712 | stitches | `stitchesjs/stitches` | styling |
| 713 | lightningcss | `parcel-bundler/lightningcss` | styling |
| 714 | graphql-request | `jasonkuhrt/graphql-request` | graphql |
| 715 | graphql-tag | `apollographql/graphql-tag` | graphql |
| 716 | graphql-tools | `ardatan/graphql-tools` | graphql |
| 717 | graphql-shield | `dimatill/graphql-shield` | graphql |
| 718 | graphql-scalars | `Urigo/graphql-scalars` | graphql |
| 719 | graphql-ws | `enisdenjo/graphql-ws` | graphql |
| 720 | graphql-sse | `enisdenjo/graphql-sse` | graphql |
| 721 | graphql-codegen | `dotansimha/graphql-code-generator` | graphql |
| 722 | graphql-mesh | `Urigo/graphql-mesh` | graphql |
| 723 | envelop | `n1ru4l/envelop` | graphql |
| 724 | genql | `remorses/genql` | graphql |
| 725 | gqty | `gqty-dev/gqty` | graphql |
| 726 | graphql-upload | `jaydenseric/graphql-upload` | graphql |
| 727 | graphql-helix | `contra/graphql-helix` | graphql |
| 728 | spectral | `stoplightio/spectral` | api-tools |
| 729 | redocly | `Redocly/redocly-cli` | api-tools |
| 730 | swagger-ui | `swagger-api/swagger-ui` | api-tools |
| 731 | swagger-jsdoc | `Surnet/swagger-jsdoc` | api-tools |
| 732 | tsoa | `lukeautry/tsoa` | api-framework |
| 733 | routing-controllers | `typestack/routing-controllers` | api-framework |
| 734 | io-ts | `gcanti/io-ts` | validation |
| 735 | runtypes | `pelotom/runtypes` | validation |
| 736 | t3-env | `t3-oss/t3-env` | validation |
| 737 | typedoc | `TypeStrong/typedoc` | documentation |
| 738 | api-extractor | `microsoft/rushstack` | documentation |
| 739 | aws-cdk | `aws/aws-cdk` | devops-infra |
| 740 | pulumi | `pulumi/pulumi` | devops-infra |
| 741 | cdktf | `hashicorp/terraform-cdk` | devops-infra |
| 742 | cdk8s | `cdk8s-team/cdk8s` | devops-infra |
| 743 | workbox | `GoogleChrome/workbox` | web-apis |
| 744 | threads | `andywer/threads.js` | web-apis |
| 745 | cross-fetch | `lquixada/cross-fetch` | data-fetching |
| 746 | serwist | `serwist/serwist` | pwa |
| 747 | vite-pwa | `vite-pwa/vite-plugin-pwa` | pwa |
| 748 | next-pwa | `shadowwalker/next-pwa` | pwa |
| 749 | lusca | `krakenjs/lusca` | security |
| 750 | hpp | `analog-nico/hpp` | security |
| 751 | csurf | `expressjs/csurf` | security |
| 752 | highland | `caolan/highland` | streams |
| 753 | through2 | `rvagg/through2` | streams |
| 754 | pump | `mafintosh/pump` | streams |
| 755 | get-stream | `sindresorhus/get-stream` | streams |
| 756 | JSONStream | `dominictarr/JSONStream` | streams |
| 757 | readable-stream | `nodejs/readable-stream` | streams |
| 758 | supports-color | `chalk/supports-color` | cli-utilities |
| 759 | strip-ansi | `chalk/strip-ansi` | cli-utilities |
| 760 | wrap-ansi | `chalk/wrap-ansi` | cli-utilities |
| 761 | ansi-escapes | `sindresorhus/ansi-escapes` | cli-utilities |
| 762 | string-width | `sindresorhus/string-width` | cli-utilities |
| 763 | cli-table3 | `cli-table/cli-table3` | cli-utilities |
| 764 | log-update | `sindresorhus/log-update` | cli-utilities |
| 765 | enquirer | `enquirer/enquirer` | cli-utilities |
| 766 | cli-spinners | `sindresorhus/cli-spinners` | cli-utilities |
| 767 | columnify | `timoxley/columnify` | cli-utilities |
| 768 | ms | `vercel/ms` | date-time |
| 769 | pretty-ms | `sindresorhus/pretty-ms` | date-time |
| 770 | spacetime | `spencermountain/spacetime` | date-time |
| 771 | timeago.js | `hustcc/timeago.js` | date-time |
| 772 | change-case | `blakeembrey/change-case` | string |
| 773 | slugify | `simov/slugify` | string |
| 774 | pluralize | `blakeembrey/pluralize` | string |
| 775 | he | `mathiasbynens/he` | string |
| 776 | entities | `fb55/entities` | string |
| 777 | autolinker | `gregjacobs/Autolinker.js` | string |
| 778 | escape-html | `component/escape-html` | string |
| 779 | fastest-validator | `icebob/fastest-validator` | validation |
| 780 | fluent-json-schema | `fastify/fluent-json-schema` | validation |
| 781 | react-icons | `react-icons/react-icons` | react-ecosystem |
| 782 | lucide | `lucide-icons/lucide` | react-ecosystem |
| 783 | iconify | `iconify/iconify` | react-ecosystem |
| 784 | tabler-icons | `tabler/tabler-icons` | react-ecosystem |
| 785 | react-use | `streamich/react-use` | react-ecosystem |
| 786 | ahooks | `alibaba/hooks` | react-ecosystem |
| 787 | usehooks-ts | `juliencrn/usehooks-ts` | react-ecosystem |
| 788 | react-helmet-async | `staylor/react-helmet-async` | react-ecosystem |
| 789 | next-themes | `pacocoursey/next-themes` | react-ecosystem |
| 790 | next-mdx-remote | `hashicorp/next-mdx-remote` | react-ecosystem |
| 791 | mdx-bundler | `kentcdodds/mdx-bundler` | react-ecosystem |
| 792 | next-safe-action | `TheEdoRan/next-safe-action` | react-ecosystem |
| 793 | velite | `zce/velite` | content |
| 794 | starlight | `withastro/starlight` | documentation |
| 795 | rspress | `web-infra-dev/rspress` | documentation |
| 796 | vocs | `wevm/vocs` | documentation |
| 797 | histoire | `histoire-dev/histoire` | documentation |
| 798 | ladle | `tajo/ladle` | documentation |
| 799 | chromatic | `chromaui/chromatic-cli` | testing |
| 800 | nuxt-content | `nuxt/content` | vue-ecosystem |
| 801 | nuxt-image | `nuxt/image` | vue-ecosystem |
| 802 | nuxt-ui | `nuxt/ui` | vue-ecosystem |
| 803 | nuxt-devtools | `nuxt/devtools` | vue-ecosystem |
| 804 | vueuse | `vueuse/vueuse` | vue-ecosystem |
| 805 | vee-validate | `logaretm/vee-validate` | vue-ecosystem |
| 806 | vue-i18n | `intlify/vue-i18n-next` | vue-ecosystem |
| 807 | pinia-plugin-persistedstate | `prazdevs/pinia-plugin-persistedstate` | vue-ecosystem |
| 808 | unhead | `unjs/unhead` | vue-ecosystem |
| 809 | unenv | `unjs/unenv` | runtime |
| 810 | hookable | `unjs/hookable` | utility |
| 811 | mlly | `unjs/mlly` | utility |
| 812 | pkg-types | `unjs/pkg-types` | utility |
| 813 | drizzle-kit | `drizzle-team/drizzle-kit-mirror` | database |
| 814 | postgres-js | `porsager/postgres` | database |
| 815 | pg-promise | `vitaly-t/pg-promise` | database |
| 816 | massive-js | `dmfay/massive-js` | database |
| 817 | objection | `vincit/objection.js` | database |
| 818 | bookshelf | `bookshelf/bookshelf` | database |
| 819 | ts-essentials | `ts-essentials/ts-essentials` | typescript |
| 820 | utility-types | `piotrwitek/utility-types` | typescript |
| 821 | emittery | `sindresorhus/emittery` | utility |
| 822 | nanoevents | `ai/nanoevents` | utility |
| 823 | rspack | `web-infra-dev/rspack` | build-tool |
| 824 | farm | `farm-fe/farm` | build-tool |
| 825 | bun | `oven-sh/bun` | runtime |
| 826 | deno | `denoland/deno` | runtime |
| 827 | oxc | `oxc-project/oxc` | build-tool |
| 828 | jiti | `unjs/jiti` | runtime |
| 829 | mitosis | `BuilderIO/mitosis` | framework |
| 830 | windicss | `windicss/windicss` | styling |
| 831 | twind | `tw-in-js/twind` | styling |
| 832 | linaria | `callstack/linaria` | styling |
| 833 | goober | `cristianbote/goober` | styling |
| 834 | stylex | `facebook/stylex` | styling |
| 835 | react-day-picker | `gpbl/react-day-picker` | ui-component |
| 836 | react-resizable-panels | `bvaughn/react-resizable-panels` | ui-component |
| 837 | react-markdown | `remarkjs/react-markdown` | ui-component |
| 838 | react-syntax-highlighter | `react-syntax-highlighter/react-syntax-highlighter` | ui-component |
| 839 | react-error-boundary | `bvaughn/react-error-boundary` | react-ecosystem |
| 840 | zustand-middleware-immer | `pmndrs/zustand` | state-management |
| 841 | nanostores | `nanostores/nanostores` | state-management |
| 842 | recoil | `facebookexperimental/Recoil` | state-management |
| 843 | legendstate | `LegendApp/legend-state` | state-management |
| 844 | rete | `retejs/rete` | ui-component |
| 845 | reactflow | `xyflow/xyflow` | ui-component |
| 846 | elkjs | `kieler/elkjs` | ui-component |
| 847 | dagre | `dagrejs/dagre` | ui-component |
| 848 | tRPC-openapi | `jlalmes/trpc-openapi` | api-tools |
| 849 | react-navigation | `react-navigation/react-navigation` | mobile |
| 850 | react-native-reanimated | `software-mansion/react-native-reanimated` | mobile |
| 851 | react-native-gesture-handler | `software-mansion/react-native-gesture-handler` | mobile |
| 852 | react-native-screens | `software-mansion/react-native-screens` | mobile |
| 853 | react-native-safe-area-context | `th3rdwave/react-native-safe-area-context` | mobile |
| 854 | react-native-svg | `software-mansion/react-native-svg` | mobile |
| 855 | react-native-vector-icons | `oblador/react-native-vector-icons` | mobile |
| 856 | react-native-paper | `callstack/react-native-paper` | mobile |
| 857 | react-native-elements | `react-native-elements/react-native-elements` | mobile |
| 858 | react-native-maps | `react-native-maps/react-native-maps` | mobile |
| 859 | react-native-vision-camera | `mrousavy/react-native-vision-camera` | mobile |
| 860 | react-native-image-picker | `react-native-image-picker/react-native-image-picker` | mobile |
| 861 | react-native-fs | `itinance/react-native-fs` | mobile |
| 862 | react-native-async-storage | `react-native-async-storage/async-storage` | mobile |
| 863 | react-native-mmkv | `mrousavy/react-native-mmkv` | mobile |
| 864 | react-native-keychain | `oblador/react-native-keychain` | mobile |
| 865 | react-native-firebase | `invertase/react-native-firebase` | mobile |
| 866 | react-native-device-info | `react-native-device-info/react-native-device-info` | mobile |
| 867 | react-native-permissions | `zoontek/react-native-permissions` | mobile |
| 868 | react-native-share | `react-native-share/react-native-share` | mobile |
| 869 | react-native-webview | `react-native-webview/react-native-webview` | mobile |
| 870 | react-native-skia | `Shopify/react-native-skia` | mobile |
| 871 | react-native-bottom-sheet | `gorhom/react-native-bottom-sheet` | mobile |
| 872 | react-native-modal | `react-native-modal/react-native-modal` | mobile |
| 873 | react-native-calendars | `wix/react-native-calendars` | mobile |
| 874 | react-native-date-picker | `henninghall/react-native-date-picker` | mobile |
| 875 | expo-router | `expo/router` | mobile |
| 876 | expo-notifications | `expo/expo` | mobile |
| 877 | expo-camera | `expo/expo` | mobile |
| 878 | expo-file-system | `expo/expo` | mobile |
| 879 | expo-av | `expo/expo` | mobile |
| 880 | expo-image | `expo/expo` | mobile |
| 881 | expo-location | `expo/expo` | mobile |
| 882 | expo-haptics | `expo/expo` | mobile |
| 883 | vuetify | `vuetifyjs/vuetify` | vue-ecosystem |
| 884 | element-plus | `element-plus/element-plus` | vue-ecosystem |
| 885 | naive-ui | `tusen-ai/naive-ui` | vue-ecosystem |
| 886 | quasar | `quasarframework/quasar` | vue-ecosystem |
| 887 | vant | `youzan/vant` | vue-ecosystem |
| 888 | arco-design-vue | `arco-design/arco-design-vue` | vue-ecosystem |
| 889 | radix-vue | `radix-vue/radix-vue` | vue-ecosystem |
| 890 | nuxt-icon | `nuxt/icon` | vue-ecosystem |
| 891 | nuxt-color-mode | `nuxt-modules/color-mode` | vue-ecosystem |
| 892 | vue-router | `vuejs/router` | vue-ecosystem |
| 893 | vue-chartjs | `apertureless/vue-chartjs` | vue-ecosystem |
| 894 | vue-echarts | `ecomfe/vue-echarts` | vue-ecosystem |
| 895 | skeleton | `skeletonlabs/skeleton` | svelte-ecosystem |
| 896 | flowbite-svelte | `themesberg/flowbite-svelte` | svelte-ecosystem |
| 897 | svelte-french-toast | `kbrgl/svelte-french-toast` | svelte-ecosystem |
| 898 | formsnap | `huntabyte/formsnap` | svelte-ecosystem |
| 899 | bits-ui | `huntabyte/bits-ui` | svelte-ecosystem |
| 900 | melt-ui | `melt-ui/melt-ui` | svelte-ecosystem |
| 901 | svelte-headless-table | `bryanmylee/svelte-headless-table` | svelte-ecosystem |
| 902 | ng-zorro-antd | `NG-ZORRO/ng-zorro-antd` | angular-ecosystem |
| 903 | ngx-bootstrap | `valor-software/ngx-bootstrap` | angular-ecosystem |
| 904 | ng-select | `ng-select/ng-select` | angular-ecosystem |
| 905 | ngrx | `ngrx/platform` | angular-ecosystem |
| 906 | ngxs | `ngxs/store` | angular-ecosystem |
| 907 | transloco | `ngneat/transloco` | angular-ecosystem |
| 908 | angular-formly | `ngx-formly/ngx-formly` | angular-ecosystem |
| 909 | apollo-angular | `kamilkisiela/apollo-angular` | angular-ecosystem |
| 910 | angular-fire | `angular/angularfire` | angular-ecosystem |
| 911 | browserslist | `browserslist/browserslist` | build-tool |
| 912 | caniuse-lite | `browserslist/caniuse-lite` | build-tool |
| 913 | autoprefixer | `postcss/autoprefixer` | css |
| 914 | cssnano | `cssnano/cssnano` | css |
| 915 | clean-css | `clean-css/clean-css` | css |
| 916 | purgecss | `FullHuman/purgecss` | css |
| 917 | critical | `addyosmani/critical` | css |
| 918 | critters | `GoogleChromeLabs/critters` | css |
| 919 | fontsource | `fontsource/fontsource` | css |
| 920 | dotenv-expand | `motdotla/dotenv-expand` | config |
| 921 | cross-spawn | `moxystudio/node-cross-spawn` | utility |
| 922 | which | `npm/node-which` | utility |
| 923 | npm-run-path | `sindresorhus/npm-run-path` | utility |
| 924 | resolve | `browserify/resolve` | utility |
| 925 | enhanced-resolve | `webpack/enhanced-resolve` | utility |
| 926 | find-up | `sindresorhus/find-up` | utility |
| 927 | locate-path | `sindresorhus/locate-path` | utility |
| 928 | pkg-dir | `sindresorhus/pkg-dir` | utility |
| 929 | escalade | `lukeed/escalade` | utility |
| 930 | yocto-queue | `sindresorhus/yocto-queue` | utility |
| 931 | p-locate | `sindresorhus/p-locate` | utility |
| 932 | p-cancelable | `sindresorhus/p-cancelable` | utility |
| 933 | is-glob | `micromatch/is-glob` | utility |
| 934 | picomatch | `micromatch/picomatch` | utility |
| 935 | micromatch | `micromatch/micromatch` | utility |
| 936 | minimatch | `isaacs/minimatch` | utility |
| 937 | braces | `micromatch/braces` | utility |
| 938 | fill-range | `jonschlinkert/fill-range` | utility |
| 939 | to-regex-range | `micromatch/to-regex-range` | utility |
| 940 | is-number | `jonschlinkert/is-number` | utility |
| 941 | enzyme | `enzymejs/enzyme` | testing |
| 942 | istanbul | `istanbuljs/istanbuljs` | testing |
| 943 | c8 | `bcoe/c8` | testing |
| 944 | nyc | `istanbuljs/nyc` | testing |
| 945 | fast-check | `dubzzz/fast-check` | testing |
| 946 | dockerode | `apocas/dockerode` | devops-infra |
| 947 | tiny-invariant | `alexreardon/tiny-invariant` | utility |
| 948 | tiny-warning | `alexreardon/tiny-warning` | utility |
| 949 | class-variance-authority | `joe-bell/cva` | styling |
| 950 | theme-ui | `system-ui/theme-ui` | styling |
| 951 | rebass | `rebassjs/rebass` | styling |
| 952 | styled-system | `styled-system/styled-system` | styling |
| 953 | debug | `debug-js/debug` | utility |
| 954 | semver | `npm/node-semver` | utility |
| 955 | signal-exit | `tapjs/signal-exit` | utility |
| 956 | graceful-fs | `isaacs/node-graceful-fs` | file |
| 957 | globrex | `terkelg/globrex` | utility |
| 958 | deferred-promise | `nicolo-ribaudo/deferred-promise` | utility |
| 959 | open | `sindresorhus/open` | utility |
| 960 | strip-json-comments | `sindresorhus/strip-json-comments` | utility |
| 961 | toml | `BinaryMuse/toml-node` | serialization |
| 962 | ini | `npm/ini` | serialization |
| 963 | dotenv-vault | `dotenv-org/dotenv-vault` | config |
| 964 | form-data | `form-data/form-data` | http-client |
| 965 | cheerio-select | `cheeriojs/cheerio-select` | scraping |
| 966 | crawlee | `apify/crawlee` | scraping |
| 967 | playwright-core | `microsoft/playwright` | testing |
| 968 | puppeteer-core | `puppeteer/puppeteer` | testing |
| 969 | happy-dom-global-registrar | `capricorn86/happy-dom` | testing |
| 970 | socket.io-adapter | `socketio/socket.io-adapter` | websocket |
| 971 | uwebsockets | `uNetworking/uWebSockets.js` | websocket |
| 972 | denokv | `denoland/denokv` | database |
| 973 | drizzle-zod | `drizzle-team/drizzle-orm` | database |
| 974 | lucia-adapter-prisma | `lucia-auth/lucia` | auth |
| 975 | hattip | `hattipjs/hattip` | server |
| 976 | listhen | `unjs/listhen` | server |
| 977 | serve-handler | `vercel/serve-handler` | server |
| 978 | http-errors | `jshttp/http-errors` | server |
| 979 | on-finished | `jshttp/on-finished` | server |
| 980 | raw-body | `stream-utils/raw-body` | server |
| 981 | accepts | `jshttp/accepts` | server |
| 982 | content-type | `jshttp/content-type` | server |
| 983 | type-is | `jshttp/type-is` | server |
| 984 | vary | `jshttp/vary` | server |
| 985 | etag | `jshttp/etag` | server |
| 986 | fresh-check | `jshttp/fresh` | server |
| 987 | range-parser | `jshttp/range-parser` | server |
| 988 | send | `pillarjs/send` | server |
| 989 | finalhandler | `pillarjs/finalhandler` | server |
| 990 | depd | `dougwilson/nodejs-depd` | utility |
| 991 | statuses | `jshttp/statuses` | server |
| 992 | merge-descriptors | `sindresorhus/merge-descriptors` | utility |
| 993 | react-native-push-notification | `zo0r/react-native-push-notification` | mobile |
| 994 | vue-flow | `bcakmakoglu/vue-flow` | vue-ecosystem |
| 995 | svelte-motion | `mattjennings/svelte-motion` | svelte-ecosystem |
| 996 | ag-grid-angular | `ag-grid/ag-grid` | angular-ecosystem |
| 997 | penthouse | `pocketjoso/penthouse` | css |
| 998 | capsize | `seek-oss/capsize` | css |
| 999 | react-test-renderer | `facebook/react` | testing |
| 1000 | v8-to-istanbul | `istanbuljs/v8-to-istanbul` | testing |