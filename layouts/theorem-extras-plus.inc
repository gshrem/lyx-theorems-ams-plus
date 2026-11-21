# SPDX-License-Identifier: GPL-2.0-or-later
# Theorems (AMS) Plus 2.0.0
# Plus modifications: Gilad Shrem <shrem173@gmail.com>, 2024-2026. See CREDITS.md.

# Additional environments by Gilad Shrem. IDs retain legacy spelling.
Format 111

Counter auxclaim
    GuiName "Auxiliary Claim"
    LaTeXName auxclaim
    Within section
    LabelString "\arabic{auxclaim}"
    RefFormat auxclaim "Auxiliary Claim|Auxiliary Claims \arabic{auxclaim}"
End





Style Examples*
	CopyStyle             Example*
  Category Examples
	LatexName             examples*
	LabelString           "Examples."
	EndLabelType          Static
	EndLabelString        "◊◊◊"
	TheoremName                 examples*
	TheoremLaTeXName            thmplusExamplesStarHeading
	TheoremStyle                thmplusRemark
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Examples
	TheoremCrossRefPluralName   Examples
	TheoremZRefName             none
	Preamble
	  \providecommand{\thmplusExamplesStarHeading}{\color{thmplusPurple}\bfseries\protect\examplesname}
	  \RequirePackage{etoolbox}
	  \AtEndEnvironment{examples*}{\thmplusExampleEnd}
	EndPreamble
	LangPreamble
		\providecommand{\examplesname}{_(Examples)}
	EndLangPreamble
	BabelPreamble
		\addto\captions$$lang{\renewcommand{\examplesname}{_(Examples)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{examples*}{_(examples)}{_(examples)}\Crefname{examples*}{_(Examples)}{_(Examples)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style CountersExample
	CopyStyle             Example
  Category Examples
	LatexName             counterexample
	LabelString           "Counterexample \thetheorem."
	EndLabelType          Static
	EndLabelString        "◊◊◊"
	TheoremName                 counterexample
	TheoremLaTeXName            thmplusCountersExampleHeading
	TheoremStyle                thmplusRemark
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Counterexample
	TheoremCrossRefPluralName   Counterexamples
	TheoremZRefName             none
	Preamble
	  \providecommand{\thmplusCountersExampleHeading}{\color{thmplusPurple}\bfseries\protect\counterexamplename}
	  \RequirePackage{etoolbox}
	  \AtEndEnvironment{counterexample}{\thmplusExampleEnd}
	EndPreamble
	LangPreamble
		\providecommand{\counterexamplename}{_(Counterexample)}
	EndLangPreamble
	BabelPreamble
		\addto\captions$$lang{\renewcommand{\counterexamplename}{_(Counterexample)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{counterexample}{_(counterexample)}{_(counterexamples)}\Crefname{counterexample}{_(Counterexample)}{_(Counterexamples)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix cex
End


Style CountersExample*
	CopyStyle             Example*
  Category Examples
	LatexName             counterexample*
	LabelString           "Counterexample."
	EndLabelType          Static
	EndLabelString        "◊◊◊"
	TheoremName                 counterexample*
	TheoremLaTeXName            thmplusCountersExampleStarHeading
	TheoremStyle                thmplusRemark
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Counterexample
	TheoremCrossRefPluralName   Counterexamples
	TheoremZRefName             none
	Preamble
	  \providecommand{\thmplusCountersExampleStarHeading}{\color{thmplusPurple}\bfseries\protect\counterexamplename}
	  \RequirePackage{etoolbox}
	  \AtEndEnvironment{counterexample*}{\thmplusExampleEnd}
	EndPreamble
	LangPreamble
		\providecommand{\counterexamplename}{_(Counterexample)}
	EndLangPreamble
	BabelPreamble
		\addto\captions$$lang{\renewcommand{\counterexamplename}{_(Counterexample)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{counterexample*}{_(counterexample)}{_(counterexamples)}\Crefname{counterexample*}{_(Counterexample)}{_(Counterexamples)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style AuxiliaryClaim
	CopyStyle             Claim
  Category Theorems
	LatexName             auxclaim
	LabelString           "Auxiliary Claim \theauxclaim"
	TheoremName                 auxclaim
	TheoremLaTeXName            thmplusAuxiliaryClaimHeading
	TheoremStyle                thmplusRemark
	TheoremCounter              ""
	TheoremParentCounter        section
	TheoremCrossRefName         "Auxiliary Claim"
	TheoremCrossRefPluralName   "Auxiliary Claims"
	TheoremZRefName             none
	Preamble
	  \providecommand{\thmplusAuxiliaryClaimHeading}{\color{thmplusCandy}\bfseries\protect\auxclaimname}
	  \AtBeginDocument{
		\renewcommand{\theauxclaim}{\arabic{auxclaim}}

		\@ifpackageloaded{hyperref}{\gdef\theHauxclaim{\theHsection.\arabic{auxclaim}}}{}

	  }
	EndPreamble
	LangPreamble
		\providecommand{\auxclaimname}{_(Auxiliary Claim)}
	EndLangPreamble
	BabelPreamble
		\addto\captions$$lang{\renewcommand{\auxclaimname}{_(Auxiliary Claim)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{auxclaim}{_(auxiliary claim)}{_(auxiliary claims)}\Crefname{auxclaim}{_(Auxiliary Claim)}{_(Auxiliary Claims)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix auxclaim
	LabelCounter auxclaim
End


Style AuxiliaryClaim*
	CopyStyle             Claim*
  Category Theorems
	LatexName             auxclaim*
	LabelString           "Auxiliary Claim."
	TheoremName                 auxclaim*
	TheoremLaTeXName            thmplusAuxiliaryClaimStarHeading
	TheoremStyle                thmplusRemark
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         "Auxiliary Claim"
	TheoremCrossRefPluralName   "Auxiliary Claims"
	TheoremZRefName             none
	Preamble
	  \providecommand{\thmplusAuxiliaryClaimStarHeading}{\color{thmplusCandy}\bfseries\protect\auxclaimname}
	EndPreamble
	LangPreamble
		\providecommand{\auxclaimname}{_(Auxiliary Claim)}
	EndLangPreamble
	BabelPreamble
		\addto\captions$$lang{\renewcommand{\auxclaimname}{_(Auxiliary Claim)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{auxclaim*}{_(auxiliary claim)}{_(auxiliary claims)}\Crefname{auxclaim*}{_(Auxiliary Claim)}{_(Auxiliary Claims)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End


Style Answer
	CopyStyle             Solution
  Category Solutions
	LatexName             answer
	LabelString           "Answer \thetheorem."
	TheoremName                 answer
	TheoremLaTeXName            answername
	TheoremStyle                thmplusDefinition
	TheoremCounter              thm
	TheoremParentCounter        ""
	TheoremCrossRefName         Answer
	TheoremCrossRefPluralName   Answers
	TheoremZRefName             none
	LangPreamble
		\providecommand{\answername}{_(Answer)}
	EndLangPreamble
	BabelPreamble
		\addto\captions$$lang{\renewcommand{\answername}{_(Answer)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{answer}{_(answer)}{_(answers)}\Crefname{answer}{_(Answer)}{_(Answers)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix ans
End


Style Answer*
	CopyStyle             Solution*
  Category Solutions
	LatexName             answer*
	LabelString           "Answer."
	TheoremName                 answer*
	TheoremLaTeXName            answername
	TheoremStyle                thmplusDefinition
	TheoremCounter              none
	TheoremParentCounter        ""
	TheoremCrossRefName         Answer
	TheoremCrossRefPluralName   Answers
	TheoremZRefName             none
	LangPreamble
		\providecommand{\answername}{_(Answer)}
	EndLangPreamble
	BabelPreamble
		\addto\captions$$lang{\renewcommand{\answername}{_(Answer)}}

    \AddToHook{begindocument/end}{%
      \ifdefined\crefname
        \ifdefined\extras$$lang\addto\extras$$lang{\crefname{answer*}{_(answer)}{_(answers)}\Crefname{answer*}{_(Answer)}{_(Answers)}}\fi
      \fi
    }
  EndBabelPreamble
	RefPrefix OFF
End
