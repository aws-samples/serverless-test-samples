# Toolchain Setup - MacOS

<!-- toc -->

- [Setup SSH](#setup-ssh)
    - [Generate KeyPairs](#generate-keypairs)
- [Xcode Command Line Tools](#xcode-command-line-tools)
- [Homebrew](#homebrew)
    - [Homebrew Packages](#homebrew-packages)
    - [macOS Applications](#macos-applications)
- [Configure Shell](#configure-shell)
- [Configure Git](#configure-git)
- [Configure VIM](#configure-vim)
- [Configure AWS SDKs and Tools](#configure-aws-sdks-and-tools)
    - [Setup AWS configuration](#setup-aws-configuration)
- [Install NodeJS](#install-nodejs)
- [Install Python](#install-python)

----

## Setup SSH

SSH is required for:

1. Connecting to Git repositories hosted on [GitFarm](https://code.amazon.com/) or
   [Gitlab](https://gitlab.aws.dev/)
2. Connecting to
   [Cloud Desktop](https://builderhub.corp.amazon.com/docs/cloud-desktop/user-guide/logging-in.html)

Please do not use SSH to connect to EC2, instead use SSM Session Manager.

### Generate KeyPairs

This process demonstrates how to generate multiple key-pairs (or identities) so that you
can use different key-pairs for services you interact with.

**Always use a pass-phrase for your key-pair**

```bash
# Create a location to store private keys
mkdir -p ~/.ssh-identities

# Create a location to store public keys
mkdir -p ~/.ssh
chmod -R 0700 ~/.ssh ~/.ssh-identities

# Generate keypair (default)
mkdir -p ~/.ssh-identities/default
ssh-keygen -q -t ecdsa -b 384 -C "$(whoami)@amzn" -f ~/.ssh-identities/default/id_ecdsa

# Copy over your default public key
cp -fv ~/.ssh-identities/default/id_ecdsa.pub ~/.ssh/id_ecdsa.pub
```

## Xcode Command Line Tools

The _Xcode Command Line Tools_ will install various compilers, system libraries, and
associated tools (`gcc`, `make`, `git`, etc.,) that are required for working with, and
installing everything else in these instructions.

To install, run the following command:

```bash
# You may be prompted to enter your password
# If you already have this installed, you will see an error and that is OK
sudo xcode-select --install
```

## Homebrew

[Homebrew](https://brew.sh/) is usually the best way to manage various tools and
software on your macOS.

To install, run the following command:

```bash
# Download the installer to /tmp
curl -fsSL -o /tmp/homebrew-install.sh -- https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh

# Verify the script
# As of January 14, 2023, the sha256 should be
# 41d5eb515a76b43e192259fde18e6cd683ea8b6a3d7873bcfc5065ab5b12235c
shasum -a 256 /tmp/homebrew-install.sh

# Run the installer
# * This is an interactive installer!
# * Unless you know what you are doing, defaults are the best
chmod +x /tmp/homebrew-install.sh
/tmp/homebrew-install.sh
```

### Homebrew Packages

Now that you have `brew` installed, let's install a few packages. The recommended method
is using a `Brewfile`. This provides you with a repeatable process as well as a
mechanism to know what you have installed and why.

Create a location to store your `Brewfile`:

```bash
mkdir -p ~/.local/etc
touch ~/.local/etc/Brewfile
```

Use this as a starting point for the contents of the `Brewfile`:

```bash
################################################################################
# Brewfile (https://github.com/Homebrew/homebrew-bundle)
################################################################################

# ------------------------------------------------------------------------------
# Taps
# ------------------------------------------------------------------------------

# Core
tap "homebrew/bundle"
tap "homebrew/cask"
tap "homebrew/core"

# Public
tap "aws/tap"
tap "isen-ng/dotnet-sdk-versions"

# ------------------------------------------------------------------------------
# Casks
# ------------------------------------------------------------------------------

# Applications
# NOTE: Comment out the one you may have already installed manually
# Casks
cask "docker"
cask "visual-studio-code"
cask "dotnet"
cask "dotnet-sdk"
cask "dotnet-sdk9-preview"
cask "dotnet-sdk8-0-200"
cask "dotnet-sdk7-0-400"
cask "dotnet-sdk6-0-400"
cask "powershell"
cask "dbeaver-community"
cask "drawio"

# ------------------------------------------------------------------------------
# Packages/Formula
# ------------------------------------------------------------------------------

#
# For more information about each package, run:
# `brew info <NAME>`
#

# Libraries (required by other tools below)
brew "expat"
brew "readline"
brew "xz"
brew "zlib"

# Tools
brew "aws-sam-cli"
brew "awscli@2"
brew "bash"
brew "git-lfs"
brew "git"
brew "jq"
brew "make"
brew "openssl@1.1"
brew "pipx"
brew "vim"
brew "checkov"

# Language installers
brew "goenv"
brew "jenv"
brew "nodenv"
brew "pyenv"
brew "poetry"
brew "rbenv"
brew "tfenv"
brew "mono"
brew "mono-libgdiplus"
brew "gcc"
brew "cmake"
brew "mingw-w64"
brew "nuget"

# Completion
brew "zsh-completions"

################################################################################
```

Let's create a utility script called `brew-up` to install/upgrade the packages defined
in our `Brewfile`:

```bash
mkdir -p ~/.local/bin
touch ~/.local/bin/brew-up
chmod +x ~/.local/bin/brew-up
```

Add the following contents to `~/.local/bin/brew-up`:

```bash
#!/usr/bin/env bash

################################################################################
# INSTALL/FRESHEN HOMEBREW PACKAGES
################################################################################

# Bash Options
set -eu
set -o pipefail

# ------------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------------

function _install {
  echo "Running brew-bundle-install [1]"
  brew bundle install || true
  echo "Running brew-bundle-install [2]"
  brew bundle install || true
  echo "Running brew-bundle-install [3]"
  brew bundle install || return 1

  return 0
}

function _upgrade {
  echo "Running brew-upgrade [1]"
  brew upgrade || true
  echo "Running brew-upgrade [2]"
  brew upgrade || true
  echo "Running brew-upgrade [3]"
  brew upgrade || return 1

  return 0
}

function _cleanup {
  echo "Running brew-autoremove [1]"
  brew autoremove || true
  echo "Running brew-autoremove [2]"
  brew autoremove || true
  echo "Running brew-autoremove [3]"
  brew autoremove || return 1

  echo "Running brew-bundle-cleanup [1]"
  brew bundle cleanup --force --zap || true
  echo "Running brew-bundle-cleanup [2]"
  brew bundle cleanup --force --zap || true
  echo "Running brew-bundle-cleanup [3]"
  brew bundle cleanup --force --zap || return 1

  echo "Running brew-cleanup [1]"
  brew cleanup -s --prune=all || true
  echo "Running brew-cleanup [2]"
  brew cleanup -s --prune=all || true
  echo "Running brew-cleanup [3]"
  brew cleanup -s --prune=all || return 1

  rm -rf "$(brew --cache)" || true

  return 0
}

# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------

# Setup Brew Configs
# https://docs.brew.sh/Manpage#environment
export HOMEBREW_BUNDLE_FILE="${HOME}/.local/etc/Brewfile"
export HOMEBREW_BUNDLE_NO_LOCK=1
export HOMEBREW_NO_ANALYTICS=1

# Find Homebrew Install
declare brew_binary
if command -v "brew" < /dev/null > /dev/null 2>&1; then
  brew_binary=$(command -v "brew")
else
  for _bip in \
    "/home/linuxbrew/.linuxbrew/bin/brew" \
    "/opt/homebrew/bin/brew" \
    "/usr/local/bin/brew"; do
    if test -f "${_bip}"; then
      brew_binary="${_bip}"
      break
    fi
  done
fi
if [[ -n "${brew_binary}" ]]; then
  echo "Found 'brew': ${brew_binary}"
else
  echo "Unable to find 'brew'" >&2
  exit 1
fi

# Initialize shell
eval "$(${brew_binary} shellenv)"

# Test Brewfile
if test -f "${HOMEBREW_BUNDLE_FILE}"; then
  echo "Using Brewfile: ${HOMEBREW_BUNDLE_FILE}"
  brew bundle list > /dev/null
else
  echo "Unable to find ${HOMEBREW_BUNDLE_FILE}" >&2
  exit 1
fi

# Do stuff
brew update \
  && _install \
  && _upgrade \
  && _cleanup \
  && brew bundle check

# Done
exit 0

################################################################################
```

Run `brew-up` to install the packages defined in our `Brewfile`. You may need to run
this multiple times to resolve dependency/cleanup errors.

```bash
~/.local/bin/brew-up
```

**NOTE**: Now that you have a `Brewfile`, use that to manage all brew-packages in the
future - (1) Update the `Brewfile` and (2) Run `brew-up`.

### macOS Applications

The `brew-up` command above should have installed _Docker_ and _Visual Studio Code_
(unless you opted not to). You will need to manually _open_ these applications one-time
to accept any EULAs.

```bash
# Launch VSCode
open "/Applications/Visual Studio Code.app"

# Launch Docker
open "/Applications/Docker.app"
```

## Configure Shell

For information on which files are read by `zsh`, please review
[zsh Startup/Shutdown Files](https://zsh.sourceforge.io/Doc/Release/Files.html).

Optionally, backup any existing shell configuration files before overwriting them:

```bash
cd ~
mkdir -p ~/.local/tmp/bak
mv "${HOME}/.zshrc" "${HOME}/.local/tmp/bak/.zshrc"
mv "${HOME}/.zprofile" "${HOME}/.local/tmp/bak/.zprofile"
```

Make sure you have a `~/.zshrc`:

```bash
touch ~/.zshrc
```

Use the following content to your `~/.zshrc`:

```bash
################################################################################
# ~/.zshrc
################################################################################

# Configure terminal
export TERM="xterm-256color"
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"

# Enable completions
autoload bashcompinit && bashcompinit
autoload -Uz compinit && compinit

# Editor
export EDITOR="vim"
export VISUAL="${EDITOR}"

# Enable Homebrew
eval "$(/opt/homebrew/bin/brew shellenv)"

# goenv/nodenv/pyenv/rbenv
for _envtool in "pyenv"; do
  if command -v "${_envtool}" > /dev/null 2>&1; then
    eval "$(${_envtool} init --path)"
  fi
done
for _envtool in "goenv" "jenv" "nodenv" "pyenv" "rbenv"; do
  if command -v "${_envtool}" > /dev/null 2>&1; then
    eval "$(${_envtool} init -)"
  fi
done

# Add ~/.local/bin to PATH
export PATH="${HOME}/.local/bin:${PATH}"

# pip configs
export PIP_REQUIRE_VIRTUALENV="true"
export PIP_DISABLE_PIP_VERSION_CHECK="true"

# Mitigate Log4J Vulnerability (Log4Shell, etc.)
export JAVA_TOOLS_OPTIONS="-Dlog4j2.formatMsgNoLookups=true"

# midway helper
function midway() {
  ~/.local/bin/midway-logout \
    && ~/.local/bin/midway-login
}

# helper to unset `AWS` environment variables
function aws-logout() {
  for _env in $(printenv | grep -iE '^AWS_' | cut -d '=' -f1); do
    unset "${_env}"
  done
}

# helper to use a specific aws profile
function aws-login() {
  local _profile="$1"

  # Unset existing
  aws-logout

  # Tell SDKs and Tools to use this profile
  export AWS_PAGER=""
  export AWS_SDK_LOAD_CONFIG=1
  export AWS_DEFAULT_PROFILE="${_profile}"
  export AWS_PROFILE="${_profile}"
}

################################################################################
```

Once you have updated your `~/.zshrc`, **please close all terminal sessions and
re-launch them for the changes to take effect**.

```bash
exec "${SHELL}"
```

## Configure Git

```bash
# Identity
git config --global user.name "FIXME_Your_git_name"
git config --global user.email "FIXME_Your_git_email"

# Editor
git config --global core.editor "vim"

# Default branch for new repos
git config --global init.defaultBranch "main"

# Verify
git config --list
```

## Configure VIM

This is a basic configuration you can use for `vim`. Use the following content in your
`~/.vimrc`:

```text
" #############################################################################
" # ~/.vimrc
" #############################################################################

" colors
set t_Co=256
syntax enable

" tabs
set tabstop=4
set softtabstop=4
set expandtab

" ui
set backspace=indent,eol,start
set cmdheight=1
set cursorline
set ignorecase
set lazyredraw
set magic
set mat=2
set number
set ruler
set showcmd
set showmatch
set smartcase

" files
filetype indent on
filetype plugin on
set encoding=utf-8
set nobackup
set noswapfile
set nowb

" No annoying sounds on errors
set noerrorbells
set novisualbell
set t_vb=
set tm=500

" git stuff
setlocal textwidth=79
setlocal colorcolumn=+1

" #############################################################################
```

## Configure AWS SDKs and Tools

### Setup AWS configuration

When working with AWS (SDK/CLI) credential and configuration information, keep the
following in mind:

1. **DO NOT** hard-code credentials in `~/.aws/config` or `~/.aws/credentials`. Instead,
   use `credential_process` OR `sso_*` configurations to dynamically fetch temporary
   credentials.
2. **DO NOT** have default configurations that authenticates AWS SDK/CLI to an account.
   This means:
    - **DO NOT** have a `[default]` profile in `~/.aws/config`. Always use _named
      profiles_ like `[profile ...]`.
    - **DO NOT** set `AWS_PROFILE` or `AWS_DEFAULT_PROFILE` in your `~/.bashrc` or
      `~/.zshrc`.
3. **DO** Always _opt-in_ to authenticating to a specific AWS Account, by explicitly
   specifying the profile or credentials.
4. **DO** have multiple _named profiles_ based on what you are using it for. For
   example, you can create a `[profile bootcamp]` that points to the AWS Account you
   will be using for this week.

Additionally:

> [default] is simply an unnamed profile. This profile is named default because it is
> the default profile used by the SDK if the user does not specify a profile. It does
> not provide inherited default values to other profiles. For example, if you set
> something in the [default] profile, and you don't set it in a named profile, then the
> value isn't set when you use the named profile.

```bash
# Create config directories
mkdir -p ~/.aws
mkdir -p ~/.aws/cli

# Create config files
touch ~/.aws/config
touch ~/.aws/cli/alias
```

Use this content as a starting point for `~/.aws/config`:

```ini
###############################################################################
# AWS CONFIG
###############################################################################
#
# Reference:
# * https://docs.aws.amazon.com/sdkref/latest/guide/overview.html
# * https://docs.aws.amazon.com/sdkref/latest/guide/settings-reference.html#ConfigFileSettings
# * https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html
#

[profile awsaccountname]
# SDK configs
defaults_mode=in-region
region=us-east-2
# CLI Configs
output=json
cli_auto_prompt=on-partial
cli_binary_format=raw-in-base64-out
cli_pager=
cli_timestamp_format=iso8601
###############################################################################
```

Use this content as a starting point for `~/.aws/cli/alias`:

```ini
###############################################################################
# AWS CLI Aliases
###############################################################################

# See: https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-alias.html

[toplevel]

whoami = sts get-caller-identity --query Arn --output text
whereami = !f(){ \
    aws iam list-account-aliases \
    --query AccountAliases[0] --output text 2>/dev/null \
    || aws sts get-caller-identity \
    --query Account --output text ; \
    aws configure get region; \
  };f

###############################################################################
```

Verify your configurations using the following commands:

```bash
# List configured profiles
aws configure list-profiles

# use the helper function to set the "awsaccountname" profile for this terminal
# In this case "awsaccountname" is the name of the profile. If you used a different
# profile name, use that instead.
aws-login "awsaccountname"

# Test
aws configure list
aws sts get-caller-identity
aws whoami
aws whereami

# Logout
aws-logout

# This should now fail since no profile/credentials are set
aws sts get-caller-identity
```

## Install NodeJS

```bash
# Install latest 20.x
# CodeBuild doesn't support 22, so we'll install 20.x
nodenv install 20.13.1
nodenv rehash

# List available
nodenv versions

# Set "system" version as global/default
nodenv global system

# Verify (these should show you "system" versions installed via brew)
nodenv which node
node --version
nodenv which npm
npm --version

npx --version
cdk --version
```

## Install Python

```bash
# Install latest 3.12.x
pyenv install 3.12.3
pyenv rehash

# List available
pyenv versions

# Set "system" version as global/default
pyenv global system

# Verify (these should show you "system" versions installed via brew)
pyenv which python3
python3 --version
pyenv which pip3
pip3 --version
```

---