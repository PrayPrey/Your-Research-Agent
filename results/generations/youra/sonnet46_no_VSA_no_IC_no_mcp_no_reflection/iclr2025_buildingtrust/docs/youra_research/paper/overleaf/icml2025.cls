% ICML 2025 LaTeX Class File
% Simplified version for local compilation
% For official submission, use the official ICML 2025 template from icml.cc

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{icml2025}[2025/01/01 ICML 2025 Submission]

% Options
\newif\if@accepted
\@acceptedfalse
\DeclareOption{accepted}{\@acceptedtrue}
\DeclareOption{final}{\@acceptedtrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

% Base class
\LoadClass[10pt,twocolumn]{article}

% Required packages
\RequirePackage{amsmath}
\RequirePackage{amssymb}
\RequirePackage{natbib}
\RequirePackage{graphicx}
\RequirePackage{hyperref}
\RequirePackage{xcolor}
\RequirePackage{algorithm}
\RequirePackage{algorithmic}
\RequirePackage{fancyhdr}

% Page layout
\RequirePackage[margin=1in]{geometry}

% Title running header
\newcommand{\icmltitlerunning}[1]{\def\@icmltitlerunning{#1}}
\icmltitlerunning{ICML 2025 Submission}

% Author handling
\newenvironment{icmlauthorlist}{}{}
\newcommand{\icmlauthor}[2]{#1}
\newcommand{\icmlsetsymbol}[2]{}
\newcommand{\icmlaffiliation}[2]{}
\newcommand{\icmlcorrespondingauthor}[2]{}

% Title command
\newcommand{\icmltitle}[1]{%
  \twocolumn[%
    \begin{center}
    {\Large\bfseries #1\par}
    \vspace{1em}
    \end{center}
  ]%
}

% Abstract
\renewenvironment{abstract}{%
  \begin{center}
  \textbf{Abstract}
  \end{center}
  \begin{quote}\small
}{%
  \end{quote}
  \vspace{1em}
}

% Affiliation printing
\newcommand{\printAffiliationsAndNotice}[1]{}

% Bibliography style
\bibliographystyle{plainnat}

% Headers
\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\small\@icmltitlerunning}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

\endinput
