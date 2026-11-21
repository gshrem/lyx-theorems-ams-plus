# SPDX-License-Identifier: GPL-2.0-or-later
# Theorems (AMS) Plus 2.0.0
# Plus modifications: Gilad Shrem <shrem173@gmail.com>, 2024-2026. See CREDITS.md.

# Shared LaTeX configuration, loaded through layout dependencies.
# The internal carrier is hidden from the layout menu by its Standard alias.
# A document-level Local Layout Preamble cannot replace this layout preamble.
Format 111
Requires xcolor, amsmath, amsthm, amssymb, etoolbox

Style ThmPlusSetup
  ObsoletedBy Standard
  Preamble
	\RequirePackage{xcolor}
	\definecolor{thmplusPen}{RGB}{4,74,122}
	\definecolor{thmplusCandy}{RGB}{234,30,99}
	\definecolor{thmplusBordeaux}{RGB}{200,5,7}
	\definecolor{thmplusTurquoise}{RGB}{0,102,102}
	\definecolor{thmplusOrange}{RGB}{255,111,0}
	\definecolor{thmplusPurple}{RGB}{186,85,211}
	\definecolor{thmplusOlive}{RGB}{150,141,0}
	\newtheoremstyle{thmplusPlain}
		{\topsep}
		{\topsep}
		{\itshape}
		{0pt}
		{\bfseries}
		{\normalfont{\bfseries{:}}}
		{5pt plus 1pt minus 1pt}
		{}
	\newtheoremstyle{boldnote}
		{\topsep}
		{\topsep}
		{\normalfont}
		{0pt}
		{\normalfont\bfseries}
		{:}
		{5pt plus 1pt minus 1pt}
		{\thmname{#1}\thmnumber{ #2}\thmnote{ (#3)}}
	% The 2024 package called this style bfnotedefinition; keep that name usable.
	\@ifundefined{th@bfnotedefinition}{\expandafter\let\csname th@bfnotedefinition\endcsname\th@boldnote}{}
	\newtheoremstyle{thmplusDefinition}
		{\topsep}
		{\topsep}
		{\normalfont}
		{0pt}
		{\bfseries}
		{\normalfont{\bfseries{:}}}
		{5pt plus 1pt minus 1pt}
		{}
	\newtheoremstyle{thmplusRemark}
		{\topsep}
		{\topsep}
		{\normalfont}
		{0pt}
		{\itshape}
		{\normalfont{\bfseries{:}}}
		{5pt plus 1pt minus 1pt}
		{}
\AtBeginDocument{
  \@ifpackageloaded{prettyref}{
    \newrefformat{thm}{\protect\theoremname~\ref{#1}}
    \newrefformat{cor}{\protect\corollaryname~\ref{#1}}
    \newrefformat{lem}{\protect\lemmaname~\ref{#1}}
    \newrefformat{prop}{\protect\propositionname~\ref{#1}}
    \newrefformat{conj}{\protect\conjecturename~\ref{#1}}
    \newrefformat{fact}{\protect\factname~\ref{#1}}
    \newrefformat{def}{\protect\definitionname~\ref{#1}}
    \newrefformat{exa}{\protect\examplename~\ref{#1}}
    \newrefformat{prob}{\protect\problemname~\ref{#1}}
    \newrefformat{exer}{\protect\exercisename~\ref{#1}}
    \newrefformat{solu}{\protect\solutionname~\ref{#1}}
    \newrefformat{rem}{\protect\remarkname~\ref{#1}}
    \newrefformat{claim}{\protect\claimname~\ref{#1}}
    \newrefformat{cri}{\protect\criterionname~\ref{#1}}
    \newrefformat{alg}{\protect\algorithmname~\ref{#1}}
    \newrefformat{axm}{\protect\axiomname~\ref{#1}}
    \newrefformat{cond}{\protect\conditionname~\ref{#1}}
    \newrefformat{notes}{\protect\notesname~\ref{#1}}
    \newrefformat{nota}{\protect\notationname~\ref{#1}}
    \newrefformat{sum}{\protect\summaryname~\ref{#1}}
    \newrefformat{ack}{\protect\acknowledgementname~\ref{#1}}
    \newrefformat{conc}{\protect\conclusionname~\ref{#1}}
    \newrefformat{assu}{\protect\assumptionname~\ref{#1}}
    \newrefformat{que}{\protect\questionname~\ref{#1}}
    \newrefformat{obs}{\protect\observationname~\ref{#1}}
    \newrefformat{cex}{\protect\counterexamplename~\ref{#1}}
    \newrefformat{auxclaim}{\protect\auxclaimname~\ref{#1}}
    \newrefformat{ans}{\protect\answername~\ref{#1}}
    \newrefformat{case}{\protect\casename~\ref{#1}}
  }{}
}
% Use amsthm line-breaking so long examples keep their end mark at the edge.
\providecommand{\thmplusExampleEnd}{\begingroup\renewcommand{\qedsymbol}{\ensuremath{\lozenge\lozenge\lozenge}}\qed\endgroup}

% cleveref has no built-in Hebrew conjunction set. Keep language switching local.
\providecommand{\thmplusHebrewConjunctions}{%
  \renewcommand{\crefpairconjunction}{ ו-}%
  \renewcommand{\crefmiddleconjunction}{, }%
  \renewcommand{\creflastconjunction}{ ו-}%
  \renewcommand{\crefrangeconjunction}{ עד }%
  \renewcommand{\crefpairgroupconjunction}{ ו-}%
  \renewcommand{\crefmiddlegroupconjunction}{, }%
  \renewcommand{\creflastgroupconjunction}{ ו-}%
}
\providecommand{\thmplusEnglishConjunctions}{%
  \renewcommand{\crefpairconjunction}{ and\nobreakspace}%
  \renewcommand{\crefmiddleconjunction}{, }%
  \renewcommand{\creflastconjunction}{ and\nobreakspace}%
  \renewcommand{\crefrangeconjunction}{ to\nobreakspace}%
  \renewcommand{\crefpairgroupconjunction}{ and\nobreakspace}%
  \renewcommand{\crefmiddlegroupconjunction}{, }%
  \renewcommand{\creflastgroupconjunction}{, and\nobreakspace}%
}
\AddToHook{begindocument/end}{%
  \@ifpackageloaded{cleveref}{%
    \ifdefined\captionshebrew\addto\captionshebrew{\thmplusHebrewConjunctions}\fi
    \ifdefined\captionsenglish\addto\captionsenglish{\thmplusEnglishConjunctions}\fi
    \ifdefstring{\languagename}{hebrew}{\thmplusHebrewConjunctions}{}%
  }{}%
}
EndPreamble
End
