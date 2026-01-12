\title{\Huge \textbf{Final Project Report}}

\maketitle

\vspace{1cm}

\begin{figure}[h]
    \centering
    \includegraphics[width=0.5\textwidth]{images/logotsp.png}
\end{figure}

\vspace{2cm}

\begin{center}
    \huge \author{Guillaume Macquart de Terline}\\[0.3cm]
    \large Network Science and Graph Learning \\[0.2cm]
    \date{}{01 Janvier 2026}
\end{center}

\newpage

\tableofcontents

\newpage

\section{Abstract}

This report includes the answers to my homework for the final project of the Network Science and Graph Learning course. The code used to perform the analysis is available in the GitHub repository: \url{https://github.com/Gdeterline/Network-Science-and-Graph-Learning}.

\section{Introduction}

\subsection{Context}

Network Science has emerged as a fundamental discipline for understanding the structure and dynamics of complex systems. From biological interactions and technological infrastructures to social relationships, graph representations allow us to model entities as nodes and their interactions as edges, revealing patterns that are not observable when analyzing individual components in isolation.

In particular, the study of online social networks such as  Facebook has gained significant traction. These networks provide a rich testing ground for algorithms in Graph Learning, such as link prediction, label propagation, and community detection. Understanding the topology of social graphs helps in analyzing information diffusion, influence maximization, and the formation of social bubbles.

This project focuses on the analysis of real-world social network data using utilizing various metrics and algorithms from the field of Graph Theory and Machine Learning. By analyzing the Facebook 100 dataset, and applying various algorithms, we aim to uncover the underlying organizational principles of these university-based social communities.

\subsection{Considered Dataset}

The dataset analyzed in this project is the well-known \textbf{Facebook 100} dataset. This collection consists of complete friendship networks from 100 American colleges and universities as they existed in September 2005. The anonymized snapshot contains the connections among $n = 1,208,316$ users, and a total of $m = 93,969,074$ edges (unweighted and undirected) between them.

The data consists of 100 graph files in GML (Graph Modeling Language) format, located in the \texttt{data/} directory. This includes networks ranging from colleges (e.g., \textit{Caltech} with 762 nodes) to larger universities (e.g., \textit{UCLA} with 20466 nodes, etc.).

Each graph represents a single university's social network:
\begin{itemize}
    \item \textbf{Nodes}: Represent individual persons (students, faculty, or staff).
    \item \textbf{Edges}: Represent "friendship" links between two individuals.
    \item \textbf{Attributes}: Nodes are typically annotated with metadata, including:
    \begin{itemize}
        \item Person's Status (Undergraduate, Graduate, Summer Student, Faculty, Staff or Alumni)
        \item Dormitory/House (if any)
        \item Major (if any)
        \item Gender (M or F)
        \item Graduation Year
    \end{itemize}
\end{itemize}

\section{Question 1: Reading}

The purpose of this question is to read and understand the following three papers:
\begin{itemize}
    \item \textit{Social structure of Facebook networks} by Traud, A. L., Mucha, P. J. \& Porter, M. A. (Physica A: Statistical Mechanics and its Applications 391, 4165 – 4180, 2012).
    The main goal of this paper is to study the social structure of Facebook networks at 100 American colleges and universities at a single point in time. The authors investigate how user attributes such as gender, major, dormitory, and graduation year influence the formation of friendship links, specifically focusing on assortativity and community structure.

    \item \textit{Comparing community structure to characteristics in online collegiate social networks} by Traud, A. L., Kelsic, E. D., Mucha, P. J. \& Porter, M. A. (SIAM Review 53, 526–543, 2011).
    This paper explores the community structure within the Facebook networks of five US universities. The study quantifies the correlation between topological communities and metadata, highlighting how different demographic factors drive clustering at different institutions.

    \item \textit{Assembling thefacebook: Using heterogeneity to understand online social network assembly} by Jacobs, A. Z., Way, S. F., Ugander, J. \& Clauset, A. (Proceedings of the ACM Web Science Conference, WebSci ’15, 18:1–18:10, 2015).
    This paper examines the evolution and assembly of the early Facebook network by analyzing the temporal sequence of user sign-ups and link formations. The authors propose a model that leverages node heterogeneity to explain the network's growth patterns and structural properties.

\end{itemize}
    

\section{Question 2: Social Network Analysis with the Facebook100 Dataset}

Let us consider three networks from the FB100 dataset: \texttt{Caltech} (with 762 nodes in the LCC), \texttt{MIT} (which has 6402 nodes in the LCC), and \texttt{Johns Hopkins} (which has 5157 nodes in the LCC).

The figures \ref{fig:degree_distribution_caltech}, \ref{fig:degree_distribution_mit}, and \ref{fig:degree_distribution_jhu} show the degree distributions for each of these three networks on a log-log scale.

\begin{figure}[H]
    \centering
    \begin{minipage}{0.32\textwidth}
        \centering
        \includegraphics[width=\textwidth]{images/caltech_degree_distribution.png}
        \caption{Degree distribution for Caltech network}
        \label{fig:degree_distribution_caltech}
    \end{minipage}\hfill
    \begin{minipage}{0.32\textwidth}
        \centering
        \includegraphics[width=\textwidth]{images/mit_degree_distribution.png}
        \caption{Degree distribution for MIT network}
        \label{fig:degree_distribution_mit}
    \end{minipage}\hfill
    \begin{minipage}{0.32\textwidth}
        \centering
        \includegraphics[width=\textwidth]{images/john_hopkins_degree_distribution.png}
        \caption{Degree distribution for Johns Hopkins network}
        \label{fig:degree_distribution_jhu}
    \end{minipage}
\end{figure}

The figures \ref{fig:degree_distribution_mit}, and \ref{fig:degree_distribution_jhu} both exhibit quite steep normal distributions, exhibiting that most nodes are of small degree, while a few others are of higher degree (hubs). In large universities, we can comprehend that as [A COMPLETER]

In contrast, the Caltech network displays a noticeably different structure (figure \ref{fig:degree_distribution_caltech}). As the smallest network in our sample (762 nodes), it is significantly denser than the others, with a bigger proportion of nodes of higher degrees. This high density suggests that the social environment at Caltech is more cohesive, with students likely knowing a larger fraction of their peers compared to the two larger institutions.


Given these three networks, we now seek to analyze their graph topologies. Thus, we seek to compute the global clustering coeﬃcient and mean local clustering coeﬃcient for each of the 3 networks. In addition, we compute the edge density of each network. The results are summarized in Table 1.

\begin{table}[ht]
\centering
\begin{tabular}{lccc}
\hline
College/University & Global Clustering Coefficient & Mean Local Clustering Coefficient & Edge Density \\
\hline
Caltech & 0.291283 & 0.409294 & 0.056404 \\
MIT & 0.180288 & 0.271219 & 0.012118 \\
John Hopkins & 0.193161 & 0.268393 & 0.013910 \\
\hline
\end{tabular}
\label{Tab:clustering_coefficients_edge_density}
\caption{Clustering Coefficients (Global and Mean Local) and Edge Density for Caltech, MIT, and Johns Hopkins networks}
\centering
\end{table}

[ANALYSIS TO COMPLETE]


To assess the similarities and differences in local structures across these networks, we scatter plot the degree versus local clustering coeﬃcient for each network node. The resulting plots are shown in Figures \ref{fig:degree_vs_clustering_caltech}, \ref{fig:degree_vs_clustering_mit}, and \ref{fig:degree_vs_clustering_jhu}.

\begin{figure}[H]
    \centering
    \begin{minipage}{0.32\textwidth}
        \centering
        \includegraphics[width=\textwidth]{images/caltech_degree_vs_local_clustering_coefficient.png}
        \caption{Degree vs Local Clustering Coefficient for Caltech network}
        \label{fig:degree_vs_clustering_caltech}
    \end{minipage}\hfill
    \begin{minipage}{0.32\textwidth}
        \centering
        \includegraphics[width=\textwidth]{images/mit_degree_vs_local_clustering_coefficient.png}
        \caption{Degree vs Local Clustering Coefficient for MIT network}
        \label{fig:degree_vs_clustering_mit}
    \end{minipage}\hfill
    \begin{minipage}{0.32\textwidth}
        \centering
        \includegraphics[width=\textwidth]{images/john_hopkins_degree_vs_local_clustering_coefficient.png}
        \caption{Degree vs Local Clustering Coefficient for Johns Hopkins network}
        \label{fig:degree_vs_clustering_jhu}
    \end{minipage}
\end{figure}

[ANALYSIS TO COMPLETE]

\section{Question 3: Assortativity Analysis with the Facebook100 Dataset}

In this section, we compute, then analyze the assortativity of all the 100 networks in the Facebook100 dataset.
