# SPDX-License-Identifier: GPL-2.0-or-later
# Theorems (AMS) Plus 2.0.0
# Plus modifications: Gilad Shrem <shrem173@gmail.com>, 2024-2026. See CREDITS.md.

# textclass definition file for custom reminder environment

Format 111

Requires enumitem, calc, twemojis

Style Reminder
  DependsOn ThmPlusSetup
	RefPrefix OFF
  Category Remarks
	Margin			First_Dynamic
	LatexType		Environment
	LatexName		reminder
	NextNoIndent		0
	LeftMargin		"MMMMM"
	ParSkip			0.4
	ItemSep			0
	TopSep			0.5
	BottomSep		0.5
	Align			Block
	LabelType		Static
	LabelString		"🔔 Reminder"
	LabelSep             	xx
	LabelFont
		Color               olive
		Series              Bold
		Shape              Italic
	EndFont
	Argument 1
		LabelString   "Topic"
		Tooltip       "Reminder topic"
		MenuString    "Reminder Topic"
		Mandatory     0
	EndArgument
	Preamble
		\usepackage{twemojis}
		\providecommand{\thmplusBell}{\raisebox{-1.5bp}{\texttwemoji{bell}}}
		\providecommand{\thmplusReminderLabel}{%
			{\Large\thmplusBell}\ \textbf{\textcolor{thmplusOlive}{\emph{\remindername}}}%
		}
		\newlist{thmplusreminderlist}{itemize}{1}
		\setlist[thmplusreminderlist]{%
			align=left,
			label=\thmplusBell,
			labelindent=0pt,
			labelsep=0.6em,
			itemindent=0pt,
			topsep=5pt,
			parsep=1pt,
			leftmargin=!,%
			labelwidth=\widthof{\thmplusReminderLabel}%
		}
		\newenvironment{reminder}[1][]
		{%
			\begin{thmplusreminderlist}
			\item[\thmplusReminderLabel\if\relax\detokenize{#1}\relax\else\ \textbf{\textcolor{thmplusOlive}{(#1)}}\fi]
		}
		{%
			\end{thmplusreminderlist}
		}
	EndPreamble
	LangPreamble
		\providecommand{\remindername}{_(Reminder)}
	EndLangPreamble
	BabelPreamble
		\addto\captions$$lang{\renewcommand{\remindername}{_(Reminder)}}
	EndBabelPreamble
End
