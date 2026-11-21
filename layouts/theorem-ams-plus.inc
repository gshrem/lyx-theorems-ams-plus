# SPDX-License-Identifier: GPL-2.0-or-later
# Theorems (AMS) Plus 2.0.0
# Plus modifications: Gilad Shrem <shrem173@gmail.com>, 2024-2026. See CREDITS.md.

# Original Author : David L. Johnson <dlj0@lehigh.edu>
# Probably broken by Jean-Marc Lasgouttes <Jean-Marc.Lasgouttes@inria.fr>
# modified and modularized by Emmanuel GUREGHIAN <gureghia@boston.bertin.fr>
# Tinkered with Sep. '07 by Paul Rubin <rubin@msu.edu>
# Modularized Jan 08 by Richard Heck <rgheck@comcast.net>

# The environments defined are :
# - Theorem
# - Corollary
# - Lemma
# - Proposition
# - Conjecture
# - Definition
# - Example
# - Problem
# - Exercise
# - Solution
# - Remark
# - Claim
# - Proof
# - Case (by inclusion)

Format 111

# Menu order within categories. Every entry is defined below or in the
# included extras file; optional layouts are never declared by the base module.
Style Definition
End

Style Definition*
End

Style Theorem
End

Style Theorem*
End

Style Lemma
End

Style Lemma*
End

Style Corollary
End

Style Corollary*
End

Style Proposition
End

Style Proposition*
End

Style Conjecture
End

Style Conjecture*
End

Style Fact
End

Style Fact*
End

Style Claim
End

Style Claim*
End

Style Proof
End

Style Case
End

Style Example
End

Style Example*
End

Style Problem
End

Style Problem*
End

Style Exercise
End

Style Exercise*
End

Style Solution
End

Style Solution*
End

Style Observation
End

Style Observation*
End

Style Remark
End

Style Remark*
End

Input theorem-common-plus.inc
OutlinerName thm "Definitions & Theorems"

Counter theorem
	GuiName Theorem
	LaTeXName thm
	RefFormat thm "Theorem|Theorems \arabic{theorem}"
	RefFormat cor "Corollary|Corollaries \arabic{theorem}"
	RefFormat lem "Lemma|Lemmas \arabic{theorem}"
	RefFormat prop "Proposition|Propositions \arabic{theorem}"
	RefFormat conj "Conjecture|Conjectures \arabic{theorem}"
	RefFormat fact "Fact|Facts \arabic{theorem}"
	RefFormat def "Definition|Definitions \arabic{theorem}"
	RefFormat exa "Example|Examples \arabic{theorem}"
	RefFormat prob "Problem|Problems \arabic{theorem}"
	RefFormat exer "Exercise|Exercises \arabic{theorem}"
	RefFormat solu "Solution|Solutions \arabic{theorem}"
	RefFormat rem "Remark|Remarks \arabic{theorem}"
	RefFormat claim "Claim|Claims \arabic{theorem}"
	RefFormat cri "Criterion|Criteria \arabic{theorem}"
	RefFormat alg "Algorithm|Algorithms \arabic{theorem}"
	RefFormat axm "Axiom|Axioms \arabic{theorem}"
	RefFormat cond "Condition|Conditions \arabic{theorem}"
	RefFormat notes "Notes|Notes \arabic{theorem}"
	RefFormat nota "Notation|Notations \arabic{theorem}"
	RefFormat sum "Summary|Summaries \arabic{theorem}"
	RefFormat ack "Acknowledgement|Acknowledgements \arabic{theorem}"
	RefFormat conc "Conclusion|Conclusions[[theorem]] \arabic{theorem}"
	RefFormat assu "Assumption|Assumptions \arabic{theorem}"
	RefFormat que "Question|Questions \arabic{theorem}"
	RefFormat obs "Observation|Observations \arabic{theorem}"
	RefFormat cex "Counterexample|Counterexamples \arabic{theorem}"
	RefFormat ans "Answer|Answers \arabic{theorem}"
End

Style Theorem
  DependsOn ThmPlusSetup
  Category Theorems
	Margin                First_Dynamic
	LatexType             Environment
	LatexName             thm
	NextNoIndent          0
	ResetArgs             1
	AddToToc              thm
	IsTocCaption          1
	Argument 1
		LabelString    "Additional Theorem Text"
		Tooltip        "Additional text appended to the theorem header"
		IsTocCaption      1
	EndArgument
	LabelSep              xx
	ParIndent             MMM
	ParSkip               0.4
	ItemSep               0.2
	TopSep                0.5
	BottomSep             0.5
	ParSep                0.3
	Align                 Block
	AlignPossible         Left
	LabelType             Static
	LabelCounter          theorem
	LabelString           "Theorem \thetheorem."
	Font
	  Shape               Italic
	  Size                Normal
	EndFont
	LabelFont
	  Shape               Up
	  Series              Bold
	EndFont
	TheoremName                 thm
	TheoremLaTeXName            theoremname
	TheoremStyle                thmplusPlain
	TheoremCounter              ""
	TheoremParentCounter        ""
	TheoremCrossRefName         Theorem
	TheoremCrossRefPluralName   Theorems
	TheoremZRefName             theorem
	LangPreamble
		\providecommand{\theoremname}{_(Theorem)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\theoremname}{_(Theorem)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{thm}{_(theorem)}{_(theorems)}\Crefname{thm}{_(Theorem)}{_(Theorems)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix thm
End


Style Theorem*
  DependsOn ThmPlusSetup
  Category Theorems
	LatexType             Environment
	Margin                First_Dynamic
	LatexName             thm*
	LabelType             Static
	LabelString           "Theorem."
	NextNoIndent          1
	ResetArgs             1
	AddToToc              thm
	IsTocCaption          1
	Argument 1
		LabelString    "Additional Theorem Text"
		Tooltip        "Additional text appended to the theorem header"
		IsTocCaption      1
	EndArgument
	LabelSep              xx
	ParIndent             MMM
	ParSkip               0.4
	ItemSep               0.2
	TopSep                0.5
	BottomSep             0.5
	ParSep                0.3
	Align                 Block
	AlignPossible         Left
	Font
	  Shape               Italic
	  Size                Normal
	EndFont
	LabelFont
	  Shape               Up
	  Series              Bold
	EndFont
	TheoremName                 thm*
	TheoremLaTeXName            thmplusTheoremStarHeading
	TheoremStyle                thmplusPlain
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Theorem
	TheoremCrossRefPluralName   Theorems
	TheoremZRefName             theorem
	Preamble
	  \providecommand{\thmplusTheoremStarHeading}{\upshape\bfseries\protect\theoremname}
	EndPreamble
	LangPreamble
	  \providecommand{\theoremname}{_(Theorem)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\theoremname}{_(Theorem)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{thm*}{_(theorem)}{_(theorems)}\Crefname{thm*}{_(Theorem)}{_(Theorems)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style Corollary
	CopyStyle             Theorem
  Category Theorems
	DependsOn             Theorem
	LatexName             cor
	LabelString           "Corollary \thetheorem."
	LabelFont
	  Shape               Up
	  Series              Bold
  	  Color               Teal
	EndFont

	TheoremName                 cor
	TheoremLaTeXName            thmplusCorollaryHeading
	TheoremStyle                thmplusPlain
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Corollary
	TheoremCrossRefPluralName   Corollaries
	TheoremZRefName             corollary
	Preamble
	  \providecommand{\thmplusCorollaryHeading}{\color{thmplusTurquoise}\protect\corollaryname}
	EndPreamble
	LangPreamble
	  \providecommand{\corollaryname}{_(Corollary)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\corollaryname}{_(Corollary)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{cor}{_(corollary)}{_(corollaries)}\Crefname{cor}{_(Corollary)}{_(Corollaries)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix cor
End


Style Corollary*
	CopyStyle             Theorem*
  Category Theorems
	LatexName             cor*
	LabelString           "Corollary."
	LabelFont
	  Shape               Up
	  Series              Bold
  	  Color               Teal
	EndFont
	TheoremName                 cor*
	TheoremLaTeXName            thmplusCorollaryStarHeading
	TheoremStyle                thmplusPlain
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Corollary
	TheoremCrossRefPluralName   Corollaries
	TheoremZRefName             corollary
	Preamble
	  \providecommand{\thmplusCorollaryStarHeading}{\color{thmplusTurquoise}\protect\corollaryname}
	EndPreamble
	LangPreamble
	  \providecommand{\corollaryname}{_(Corollary)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\corollaryname}{_(Corollary)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{cor*}{_(corollary)}{_(corollaries)}\Crefname{cor*}{_(Corollary)}{_(Corollaries)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style Lemma
	CopyStyle             Theorem
  Category Theorems
	DependsOn             Theorem
	LatexName             lem
	LabelString           "Lemma \thetheorem."
	LabelFont
  	  Color               Orange
	EndFont
	TheoremName                 lem
	TheoremLaTeXName            thmplusLemmaHeading
	TheoremStyle                thmplusPlain
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Lemma
	TheoremCrossRefPluralName   Lemmas
	TheoremZRefName             lemma
	Preamble
	  \providecommand{\thmplusLemmaHeading}{\color{thmplusOrange}\protect\lemmaname}
	EndPreamble
	LangPreamble
	  \providecommand{\lemmaname}{_(Lemma)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\lemmaname}{_(Lemma)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{lem}{_(lemma)}{_(lemmas)}\Crefname{lem}{_(Lemma)}{_(Lemmas)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix lem
End


Style Lemma*
	CopyStyle             Theorem*
  Category Theorems
	LatexName             lem*
	LabelString           "Lemma."
	LabelFont
	  Shape               Up
	  Series              Bold
  	  Color               Orange
	EndFont
	TheoremName                 lem*
	TheoremLaTeXName            thmplusLemmaStarHeading
	TheoremStyle                thmplusPlain
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Lemma
	TheoremCrossRefPluralName   Lemmas
	TheoremZRefName             lemma
	Preamble
	  \providecommand{\thmplusLemmaStarHeading}{\color{thmplusOrange}\protect\lemmaname}
	EndPreamble
	LangPreamble
	  \providecommand{\lemmaname}{_(Lemma)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\lemmaname}{_(Lemma)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{lem*}{_(lemma)}{_(lemmas)}\Crefname{lem*}{_(Lemma)}{_(Lemmas)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style Proposition
	CopyStyle             Theorem
  Category Theorems
	DependsOn             Theorem
	LatexName             prop
	LabelString           "Proposition \thetheorem."
	TheoremName                 prop
	TheoremLaTeXName            propositionname
	TheoremStyle                thmplusPlain
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Proposition
	TheoremCrossRefPluralName   Propositions
	TheoremZRefName             proposition
	LangPreamble
	  \providecommand{\propositionname}{_(Proposition)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\propositionname}{_(Proposition)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{prop}{_(proposition)}{_(propositions)}\Crefname{prop}{_(Proposition)}{_(Propositions)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix prop
End


Style Proposition*
	CopyStyle             Theorem*
  Category Theorems
	LatexName             prop*
	LabelString           "Proposition."
	TheoremName                 prop*
	TheoremLaTeXName            propositionname
	TheoremStyle                thmplusPlain
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Proposition
	TheoremCrossRefPluralName   Propositions
	TheoremZRefName             proposition
	LangPreamble
	  \providecommand{\propositionname}{_(Proposition)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\propositionname}{_(Proposition)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{prop*}{_(proposition)}{_(propositions)}\Crefname{prop*}{_(Proposition)}{_(Propositions)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style Conjecture
	CopyStyle             Theorem
  Category Theorems
	DependsOn             Theorem
	LatexName             conjecture
	LabelString           "Conjecture \thetheorem."
	TheoremName                 conjecture
	TheoremLaTeXName            conjecturename
	TheoremStyle                thmplusPlain
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Conjecture
	TheoremCrossRefPluralName   Conjectures
	TheoremZRefName             none
	LangPreamble
	  \providecommand{\conjecturename}{_(Conjecture)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\conjecturename}{_(Conjecture)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{conjecture}{_(conjecture)}{_(conjectures)}\Crefname{conjecture}{_(Conjecture)}{_(Conjectures)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix conj
End


Style Conjecture*
	CopyStyle             Theorem*
  Category Theorems
	LatexName             conjecture*
	LabelString           "Conjecture."
	TheoremName                 conjecture*
	TheoremLaTeXName            conjecturename
	TheoremStyle                thmplusPlain
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Conjecture
	TheoremCrossRefPluralName   Conjectures
	TheoremZRefName             none
	LangPreamble
	  \providecommand{\conjecturename}{_(Conjecture)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\conjecturename}{_(Conjecture)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{conjecture*}{_(conjecture)}{_(conjectures)}\Crefname{conjecture*}{_(Conjecture)}{_(Conjectures)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style Fact
	CopyStyle             Theorem
  Category Theorems
	DependsOn             Theorem
	LatexName             fact
	LabelString           "Fact \thetheorem."
	TheoremName                 fact
	TheoremLaTeXName            factname
	TheoremStyle                thmplusPlain
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Fact
	TheoremCrossRefPluralName   Facts
	TheoremZRefName             none
	LangPreamble
	  \providecommand{\factname}{_(Fact)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\factname}{_(Fact)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{fact}{_(fact)}{_(facts)}\Crefname{fact}{_(Fact)}{_(Facts)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix fact
End


Style Fact*
	CopyStyle             Theorem*
  Category Theorems
	LatexName             fact*
	LabelString           "Fact."
	TheoremName                 fact*
	TheoremLaTeXName            factname
	TheoremStyle                thmplusPlain
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Fact
	TheoremCrossRefPluralName   Facts
	TheoremZRefName             none
	LangPreamble
	  \providecommand{\factname}{_(Fact)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\factname}{_(Fact)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{fact*}{_(fact)}{_(facts)}\Crefname{fact*}{_(Fact)}{_(Facts)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style Definition
	CopyStyle             Theorem
  Category Definitions
	DependsOn             Theorem
	LatexName             defn
	LabelString           "Definition \thetheorem."
	Font
	  Shape               Up
	EndFont
	LabelFont
	  Shape               Up
	  Series              Bold
	  Color               Blue
	EndFont
	TheoremName                 defn
	TheoremLaTeXName            thmplusDefinitionHeading
	TheoremStyle                boldnote
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Definition
	TheoremCrossRefPluralName   Definitions
	TheoremZRefName             definition
	Preamble
	  \providecommand{\thmplusDefinitionHeading}{\color{thmplusPen}\protect\definitionname}
	EndPreamble
	LangPreamble
	  \providecommand{\definitionname}{_(Definition)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\definitionname}{_(Definition)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{defn}{_(definition)}{_(definitions)}\Crefname{defn}{_(Definition)}{_(Definitions)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix def
End


Style Definition*
	CopyStyle             Theorem*
  Category Definitions
	LatexName             defn*
#LabelType             Static
	LabelString           "Definition."
	Font
	  Shape               Up
	EndFont
	LabelFont
	  Shape               Up
	  Series              Bold
	  Color               Blue
	EndFont
	TheoremName                 defn*
	TheoremLaTeXName            thmplusDefinitionStarHeading
	TheoremStyle                boldnote
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Definition
	TheoremCrossRefPluralName   Definitions
	TheoremZRefName             definition
	Preamble
	  \providecommand{\thmplusDefinitionStarHeading}{\color{thmplusPen}\protect\definitionname}
	EndPreamble
	LangPreamble
	  \providecommand{\definitionname}{_(Definition)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\definitionname}{_(Definition)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{defn*}{_(definition)}{_(definitions)}\Crefname{defn*}{_(Definition)}{_(Definitions)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style Example
	CopyStyle             Definition
  Category Examples
	LatexName             example
	LabelString           "Example \thetheorem."
	EndLabelType          Static
	EndLabelString        "◊◊◊"
	Font
	  Shape               Up
	  Size                Normal
 	  Color               none
	EndFont
	LabelFont
	  Series              Bold
	  Shape               Italic
  	  Color               Purple
	EndFont
	TheoremName                 example
	TheoremLaTeXName            thmplusExampleHeading
	TheoremStyle                thmplusRemark
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Example
	TheoremCrossRefPluralName   Examples
	TheoremZRefName             none
	Preamble
	  \providecommand{\thmplusExampleHeading}{\color{thmplusPurple}\bfseries\protect\examplename}
	  \RequirePackage{etoolbox}
	  \AtEndEnvironment{example}{\thmplusExampleEnd}
	EndPreamble
	LangPreamble
	  \providecommand{\examplename}{_(Example)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\examplename}{_(Example)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{example}{_(example)}{_(examples)}\Crefname{example}{_(Example)}{_(Examples)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix exa
End


Style Example*
	CopyStyle             Definition*
  Category Examples
	LatexName             example*
	LabelString           "Example."
	EndLabelType          Static
	EndLabelString        "◊◊◊"
	Font
	  Shape               Up
	  Size                Normal
 	  Color               none
	EndFont
	LabelFont
	  Series              Bold
	  Shape               Italic
  	  Color               Purple
	EndFont
	TheoremName                 example*
	TheoremLaTeXName            thmplusExampleStarHeading
	TheoremStyle                thmplusRemark
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Example
	TheoremCrossRefPluralName   Examples
	TheoremZRefName             none
	Preamble
	  \providecommand{\thmplusExampleStarHeading}{\color{thmplusPurple}\bfseries\protect\examplename}
	  \RequirePackage{etoolbox}
	  \ifdefined\thmplusExampleStarEndHookAdded\else
	  \AtEndEnvironment{example*}{\thmplusExampleEnd}
	  \let\thmplusExampleStarEndHookAdded\empty
	  \fi
	EndPreamble
	LangPreamble
	  \providecommand{\examplename}{_(Example)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\examplename}{_(Example)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{example*}{_(example)}{_(examples)}\Crefname{example*}{_(Example)}{_(Examples)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style Problem
	CopyStyle             Definition
  Category Problems
	LatexName             problem
	LabelString           "Problem \thetheorem."
	LabelFont
	  Series              Bold
	  Shape               Up
  	  Color               none
	EndFont
	TheoremName                 problem
	TheoremLaTeXName            problemname
	TheoremStyle                thmplusDefinition
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Problem
	TheoremCrossRefPluralName   Problems
	TheoremZRefName             none
	LangPreamble
	  \providecommand{\problemname}{_(Problem)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\problemname}{_(Problem)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{problem}{_(problem)}{_(problems)}\Crefname{problem}{_(Problem)}{_(Problems)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix prob
End


Style Problem*
	CopyStyle             Definition*
  Category Problems
	LatexName             problem*
	LabelString           "Problem."
	LabelFont
	  Series              Bold
	  Shape               Up
  	  Color               none
	EndFont
	TheoremName                 problem*
	TheoremLaTeXName            problemname
	TheoremStyle                thmplusDefinition
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Problem
	TheoremCrossRefPluralName   Problems
	TheoremZRefName             none
	LangPreamble
	  \providecommand{\problemname}{_(Problem)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\problemname}{_(Problem)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{problem*}{_(problem)}{_(problems)}\Crefname{problem*}{_(Problem)}{_(Problems)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style Exercise
	CopyStyle             Definition
  Category Problems
	LatexName             xca
	LabelString           "Exercise \thetheorem."
	LabelFont
	  Series              Bold
	  Shape               Up
  	  Color               none
	EndFont
	TheoremName                 xca
	TheoremLaTeXName            exercisename
	TheoremStyle                thmplusDefinition
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Exercise
	TheoremCrossRefPluralName   Exercises
	TheoremZRefName             exercise
	LangPreamble
	  \providecommand{\exercisename}{_(Exercise)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\exercisename}{_(Exercise)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{xca}{_(exercise)}{_(exercises)}\Crefname{xca}{_(Exercise)}{_(Exercises)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix exer
End


Style Exercise*
	CopyStyle             Definition*
  Category Problems
	LatexName             xca*
	LabelString           "Exercise."
	LabelFont
	  Series              Bold
	  Shape               Up
  	  Color               none
	EndFont
	TheoremName                 xca*
	TheoremLaTeXName            exercisename
	TheoremStyle                thmplusDefinition
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Exercise
	TheoremCrossRefPluralName   Exercises
	TheoremZRefName             exercise
	LangPreamble
	  \providecommand{\exercisename}{_(Exercise)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\exercisename}{_(Exercise)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{xca*}{_(exercise)}{_(exercises)}\Crefname{xca*}{_(Exercise)}{_(Exercises)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style Solution
	CopyStyle             Definition
  Category Solutions
	LatexName             sol
	LabelString           "Solution \thetheorem."
	LabelFont
	  Series              Bold
	  Shape               Up
  	  Color               none
	EndFont
	TheoremName                 sol
	TheoremLaTeXName            solutionname
	TheoremStyle                thmplusDefinition
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Solution
	TheoremCrossRefPluralName   Solutions
	TheoremZRefName             solution
	LangPreamble
		\providecommand{\solutionname}{_(Solution)}
	EndLangPreamble
	BabelPreamble
		\addto\captions$$lang{\renewcommand{\solutionname}{_(Solution)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{sol}{_(solution)}{_(solutions)}\Crefname{sol}{_(Solution)}{_(Solutions)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix solu
End


Style Solution*
	CopyStyle             Definition*
  Category Solutions
	LatexName             sol*
	LabelString           "Solution."
	LabelFont
	  Series              Bold
	  Shape               Up
  	  Color               none
	EndFont
	TheoremName                 sol*
	TheoremLaTeXName            solutionname
	TheoremStyle                thmplusDefinition
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Solution
	TheoremCrossRefPluralName   Solutions
	TheoremZRefName             solution
	LangPreamble
	  \providecommand{\solutionname}{_(Solution)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\solutionname}{_(Solution)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{sol*}{_(solution)}{_(solutions)}\Crefname{sol*}{_(Solution)}{_(Solutions)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style Remark
	CopyStyle             Theorem
  Category Remarks
	DependsOn             Theorem
	LatexName             rem
	LabelString           "Remark \thetheorem."
	Font
	  Shape               Up
	  Size                Normal
	  Color               none
	EndFont
	LabelFont
	  Series              Bold
	  Shape               Italic
	  Color               Red
	EndFont
	TheoremName                 rem
	TheoremLaTeXName            thmplusRemarkHeading
	TheoremStyle                thmplusRemark
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Remark
	TheoremCrossRefPluralName   Remarks
	TheoremZRefName             none
	Preamble
	  \providecommand{\thmplusRemarkHeading}{\color{red}\bfseries\protect\remarkname}
	EndPreamble
	LangPreamble
	  \providecommand{\remarkname}{_(Remark)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\remarkname}{_(Remark)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{rem}{_(remark)}{_(remarks)}\Crefname{rem}{_(Remark)}{_(Remarks)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix rem
End


Style Remark*
	CopyStyle             Theorem*
  Category Remarks
	LatexName             rem*
	LabelString           "Remark."
	Font
	  Shape               Up
	  Size                Normal
	  Color               none
	EndFont
	LabelFont
	  Series              Bold
	  Shape               Italic
	  Color               Red
	EndFont
	TheoremName                 rem*
	TheoremLaTeXName            thmplusRemarkStarHeading
	TheoremStyle                thmplusRemark
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Remark
	TheoremCrossRefPluralName   Remarks
	TheoremZRefName             none
	Preamble
	  \providecommand{\thmplusRemarkStarHeading}{\color{red}\bfseries\protect\remarkname}
	EndPreamble
	LangPreamble
	  \providecommand{\remarkname}{_(Remark)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\remarkname}{_(Remark)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{rem*}{_(remark)}{_(remarks)}\Crefname{rem*}{_(Remark)}{_(Remarks)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style Claim
	CopyStyle             Remark
  Category Theorems
	LatexName             claim
	LabelString           "Claim \thetheorem."
	LabelFont
	  Series              Bold
	  Shape               Italic
	  Color               Magenta
	EndFont
	TheoremName                 claim
	TheoremLaTeXName            thmplusClaimHeading
	TheoremStyle                thmplusRemark
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Claim
	TheoremCrossRefPluralName   Claims
	TheoremZRefName             none
	Preamble
	  \providecommand{\thmplusClaimHeading}{\color{thmplusCandy}\bfseries\protect\claimname}
	EndPreamble
	LangPreamble
	  \providecommand{\claimname}{_(Claim)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\claimname}{_(Claim)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{claim}{_(claim)}{_(claims)}\Crefname{claim}{_(Claim)}{_(Claims)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix claim
End


Style Claim*
	CopyStyle             Remark*
  Category Theorems
	LatexName             claim*
	LabelString           "Claim."
	LabelFont
	  Series              Bold
	  Shape               Italic
	  Color               Magenta
	EndFont
	TheoremName                 claim*
	TheoremLaTeXName            thmplusClaimStarHeading
	TheoremStyle                thmplusRemark
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Claim
	TheoremCrossRefPluralName   Claims
	TheoremZRefName             none
	Preamble
	  \providecommand{\thmplusClaimStarHeading}{\color{thmplusCandy}\bfseries\protect\claimname}
	EndPreamble
	LangPreamble
	  \providecommand{\claimname}{_(Claim)}
	EndLangPreamble
	BabelPreamble
	  \addto\captions$$lang{\renewcommand{\claimname}{_(Claim)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{claim*}{_(claim)}{_(claims)}\Crefname{claim*}{_(Claim)}{_(Claims)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


# Proof retains the filled QED symbol.
Style Proof
  DependsOn ThmPlusSetup
	RefPrefix OFF
  Category Proofs
	Margin                First_Dynamic
	LatexType             Environment
	LatexName             proof
	NextNoIndent          1
	ResetArgs             1
	Argument 1
		LabelString   "Alternative Proof String"
		Tooltip       "Alternative proof string"
	EndArgument
	LabelSep              xx
	ParIndent             MMM
	ParSkip               0.4
	ItemSep               0.2
	TopSep                0.7
	BottomSep             0.7
	ParSep                0.3
	Align                 Block
	AlignPossible         Block, Left
	LabelType             Static
	LabelString           "Proof."
	EndLabelType          Box
	Font
	  Shape               Up
	  Size                Normal
	EndFont
	LabelFont
	  Shape               Italic
	EndFont
End

ModifyStyle Proof
  Requires amssymb
  Preamble
    \renewcommand*\qedsymbol{$\blacksquare$}
  EndPreamble
  EndLabelType Filled_Box
  LangPreamble
    \renewcommand{\proofname}{_(Proof)}
  EndLangPreamble
  BabelPreamble
    \addto\captions$$lang{\renewcommand{\proofname}{_(Proof)}}
  EndBabelPreamble
End

# Case list, including four levels and reference metadata.
Counter casei
	GuiName Case
	LaTeXName casenvi
	RefFormat case "Case|Cases \arabic{casei}"
	LabelString "Case \arabic{casei}."
End
Counter caseii
	GuiName Case
	LaTeXName casenvii
	RefFormat case "Case|Cases \Alph{caseii}"
	Within casei
	LabelString "Case \Alph{caseii}."
End
Counter caseiii
	GuiName Case
	LaTeXName casenviii
	RefFormat case "Case|Cases \alph{caseiii}"
	Within caseii
	LabelString "Case \alph{caseiii}."
End
Counter caseiv
	GuiName Case
	LaTeXName casenviv
	RefFormat case "Case|Cases \roman{caseiv}"
        Within caseiii
        LabelString "Case \roman{caseiv}."
End

Style Case
  DependsOn ThmPlusSetup
  RefPrefix case
  Category Proofs
  Margin                Static
  LatexType             Item_Environment
  LatexName             casenv
  LabelType             Enumerate
  LeftMargin            "Case ###."
  LabelSep              xx
  ParSkip               0.0
  ItemSep               0.2
  TopSep                0.7
  BottomSep             0.7
  ParSep                0.3
  Align                 Block
  AlignPossible         Block, Left
  LabelCounter          case
  LabelFont
    Series              Medium
    Shape               Italic
  EndFont
  HTMLTag               ol
  HTMLItem              li
  HTMLLabel             NONE
  Argument item:1
    LabelString   "Custom Item|s"
    Tooltip       "A customized item string"
  EndArgument
  NextNoIndent          1
	Requires enumitem
	# It'd be easier to use \setlist[caseenv] here, but that causes problems
	# if you nest an ordinary list inside a case environment. See discussion
	# at bug #7611.
  Preamble
    % A direction wrapper only when a language package provides it.
    \providecommand{\thmplusCaseMark}[1]{\ifdefined\textenglish\textenglish{#1}\else#1\fi}
    % Keep the third-level label and reference Latin even in Hebrew.
    \ExplSyntaxOn
    \cs_new:Npn \thmplusCaseAlphValue #1 { \int_to_alph:n {#1} }
    \cs_new:Npn \thmplusCaseAlph #1 { \exp_args:Nc \thmplusCaseAlphValue {c@#1} }
    \ExplSyntaxOff
    \AddEnumerateCounter{\thmplusCaseAlph}{\thmplusCaseAlphValue}{m}
    \newlist{casenv}{enumerate}{4}
    \setlist[casenv]{leftmargin=*,align=left,widest={iiii},labelsep=1.15em}
    \setlist[casenv,1]{label={{\itshape\casename} \arabic*.},ref=\arabic*}
    \setlist[casenv,2]{label={{\itshape\casename} \Alph*.},ref=\Alph*}
    % Punctuation follows the surrounding direction, outside the LTR marker.
    \setlist[casenv,3]{label={{\itshape\casename} \thmplusCaseMark{\thmplusCaseAlph*}.},ref=\thmplusCaseAlph*}
    \setlist[casenv,4]{label={{\itshape\casename} \thmplusCaseMark{\roman*}.},ref=\roman*}
    % Register before cleveref constructs its reference formats.
    \AddToHook{package/cleveref/after}{
      \crefname{casenvi}{\thmpluscaseName}{\thmpluscasesName}
      \Crefname{casenvi}{\casename}{\thmplusCasesName}
      \crefname{casenvii}{\thmpluscaseName}{\thmpluscasesName}
      \Crefname{casenvii}{\casename}{\thmplusCasesName}
      \crefname{casenviii}{\thmpluscaseName}{\thmpluscasesName}
      \Crefname{casenviii}{\casename}{\thmplusCasesName}
      \crefname{casenviv}{\thmpluscaseName}{\thmpluscasesName}
      \Crefname{casenviv}{\casename}{\thmplusCasesName}
    }
    % refstyle: LyX generates formatted references for theorems, not for this list.
    \@ifpackageloaded{refstyle}{%
      \newref{case}{name=\thmpluscaseName~, names=\thmpluscasesName~,
        Name=\casename~, Names=\thmplusCasesName~,
        rngtxt=\RSrngtxt, lsttwotxt=\RSlsttwotxt, lsttxt=\RSlsttxt}%
    }{}
  EndPreamble
  LangPreamble
    \providecommand{\thmpluscaseName}{_(case)}
    \providecommand{\thmpluscasesName}{_(cases)}
    \providecommand{\thmplusCasesName}{_(Cases)}
    \providecommand{\casename}{_(Case)}
  EndLangPreamble
  BabelPreamble
    \addto\captions$$lang{\renewcommand{\thmpluscaseName}{_(case)}}
    \addto\captions$$lang{\renewcommand{\thmpluscasesName}{_(cases)}}
    \addto\captions$$lang{\renewcommand{\thmplusCasesName}{_(Cases)}}
    \addto\captions$$lang{\renewcommand{\casename}{_(Case)}}
  EndBabelPreamble
End

# The legacy numbered base also provided Diagnosis.
Style Observation
  CopyStyle             Remark
  Category Remarks
  DependsOn             Remark
  LatexName             observation
  LabelString           "Observation \thetheorem."
  Font
    Shape               Up
    Size                Normal
    Color               none
  EndFont
  LabelFont
    Series              Bold
    Shape               Italic
    Color               Brown
  EndFont
	TheoremName                 observation
	TheoremLaTeXName            thmplusObservationHeading
	TheoremStyle                thmplusRemark
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Observation
	TheoremCrossRefPluralName Observations
	TheoremZRefName             none
	Preamble
	  \providecommand{\thmplusObservationHeading}{\color{thmplusBordeaux}\bfseries\protect\observationname}
	EndPreamble
  LangPreamble
    \providecommand{\observationname}{_(Observation)}
  EndLangPreamble
  BabelPreamble
    \addto\captions$$lang{\renewcommand{\observationname}{_(Observation)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{observation}{_(observation)}{_(observations)}\Crefname{observation}{_(Observation)}{_(Observations)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix obs
End

# Shared with Unnumbered Plus for legacy Diagnosis* documents.
Style Observation*
  CopyStyle             Remark*
  Category Remarks
  DependsOn             Remark*
  LatexName             observation*
  LabelString           "Observation."
  Font
    Shape               Up
    Size                Normal
    Color               none
  EndFont
  LabelFont
    Series              Bold
    Shape               Italic
    Color               Brown
  EndFont
	TheoremName                 observation*
	TheoremLaTeXName            thmplusObservationStarHeading
	TheoremStyle                thmplusRemark
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Observation
	TheoremCrossRefPluralName Observations
	TheoremZRefName             none
	Preamble
	  \providecommand{\thmplusObservationStarHeading}{\color{thmplusBordeaux}\bfseries\protect\observationname}
	EndPreamble
  LangPreamble
    \providecommand{\observationname}{_(Observation)}
  EndLangPreamble
  BabelPreamble
    \addto\captions$$lang{\renewcommand{\observationname}{_(Observation)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{observation*}{_(observation)}{_(observations)}\Crefname{observation*}{_(Observation)}{_(Observations)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End
