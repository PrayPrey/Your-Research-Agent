%%% ICML 2025 Bibliography Style (simplified natbib-based)
%%% Based on plainnat.bst with ICML modifications

ENTRY
  { address author booktitle chapter edition editor howpublished
    institution journal key month note number organization pages
    publisher school series title type volume year url }
  {}
  { label extra.label sort.label short.list }

INTEGERS { output.state before.all mid.sentence after.sentence after.block }

FUNCTION {init.state.consts}
{ #0 'before.all :=
  #1 'mid.sentence :=
  #2 'after.sentence :=
  #3 'after.block :=
}

STRINGS { s t }

FUNCTION {output.nonnull}
{ 's :=
  output.state mid.sentence =
    { ", " * write$ }
    { output.state after.block =
        { add.period$ write$
          newline$
          "\newblock " write$
        }
        { output.state before.all =
            'write$
            { add.period$ " " * write$ }
          if$
        }
      if$
      mid.sentence 'output.state :=
    }
  if$
  s
}

FUNCTION {output}
{ duplicate$ empty$
    'pop$
    'output.nonnull
  if$
}

FUNCTION {output.check}
{ 't :=
  duplicate$ empty$
    { pop$ "empty " t * " in " * cite$ * warning$ }
    'output.nonnull
  if$
}

FUNCTION {fin.entry}
{ add.period$
  write$
  newline$
}

FUNCTION {new.block}
{ output.state before.all =
    'skip$
    { after.block 'output.state := }
  if$
}

FUNCTION {new.sentence}
{ output.state after.block =
    'skip$
    { output.state before.all =
        'skip$
        { after.sentence 'output.state := }
      if$
    }
  if$
}

FUNCTION {not}
{   { #0 }
    { #1 }
  if$
}

FUNCTION {and}
{   'skip$
    { pop$ #0 }
  if$
}

FUNCTION {or}
{   { pop$ #1 }
    'skip$
  if$
}

FUNCTION {field.or.null}
{ duplicate$ empty$
    { pop$ "" }
    'skip$
  if$
}

FUNCTION {emphasize}
{ duplicate$ empty$
    { pop$ "" }
    { "{\em " swap$ * "}" * }
  if$
}

INTEGERS { nameptr nameslot maxnames numnames }

FUNCTION {format.names}
{ 's :=
  #1 'nameptr :=
  s num.names$ 'numnames :=
  numnames 'maxnames :=
  { nameptr maxnames #10 < }
    { s nameptr "{f.~}{vv~}{ll}{, jj}" format.name$ 't :=
      nameptr #1 >
        { nameptr #1 + numnames =
            { " and " * t * }
            { ", " * t * }
          if$
        }
        't
      if$
      nameptr #1 + 'nameptr :=
    }
  while$
}

FUNCTION {format.authors}
{ author empty$
    { "" }
    { author format.names }
  if$
}

FUNCTION {format.title}
{ title empty$
    { "" }
    { title "t" change.case$ }
  if$
}

FUNCTION {format.journal.vol.year}
{ journal empty$
    { "" }
    { journal emphasize
      volume empty$
        'skip$
        { ", " * volume * }
      if$
      year empty$
        'skip$
        { " (" * year * ")" * }
      if$
    }
  if$
}

FUNCTION {format.booktitle}
{ booktitle empty$
    { "" }
    { "In " booktitle emphasize * }
  if$
}

FUNCTION {format.pages}
{ pages empty$
    { "" }
    { "pp.~" pages * }
  if$
}

FUNCTION {article}
{ output.bibitem
  format.authors "author" output.check
  new.block
  format.title "title" output.check
  new.block
  format.journal.vol.year "journal" output.check
  format.pages output
  fin.entry
}

FUNCTION {book}
{ output.bibitem
  format.authors "author" output.check
  new.block
  title emphasize "title" output.check
  publisher "publisher" output.check
  year "year" output.check
  fin.entry
}

FUNCTION {inproceedings}
{ output.bibitem
  format.authors "author" output.check
  new.block
  format.title "title" output.check
  new.block
  format.booktitle "booktitle" output.check
  format.pages output
  year "year" output.check
  fin.entry
}

FUNCTION {misc}
{ output.bibitem
  format.authors output
  title output
  howpublished output
  year output
  note output
  fin.entry
}

FUNCTION {default.type} { misc }

MACRO {jan} {"January"}
MACRO {feb} {"February"}
MACRO {mar} {"March"}
MACRO {apr} {"April"}
MACRO {may} {"May"}
MACRO {jun} {"June"}
MACRO {jul} {"July"}
MACRO {aug} {"August"}
MACRO {sep} {"September"}
MACRO {oct} {"October"}
MACRO {nov} {"November"}
MACRO {dec} {"December"}

READ

FUNCTION {sortify}
{ purify$
  "l" change.case$
}

INTEGERS { len }

FUNCTION {chop.word}
{ 's :=
  'len :=
  s #1 len substring$ =
    { s len #1 + global.max$ substring$ }
    's
  if$
}

FUNCTION {sort.format.names}
{ 's :=
  #1 'nameptr :=
  ""
  s num.names$ 'numnames :=
  numnames 'maxnames :=
  { nameptr maxnames < }
    { s nameptr "{vv{ } }{ll{ }}{  f{ }}{  jj{ }}" format.name$ 't :=
      nameptr #1 >
        { "   " * t sortify * }
        { t sortify * }
      if$
      nameptr #1 + 'nameptr :=
    }
  while$
}

FUNCTION {sort.format.title}
{ 't :=
  "A " #2
    "An " #3
      "The " #4 t chop.word
    chop.word
  chop.word
  sortify
  #1 global.max$ substring$
}

FUNCTION {author.sort}
{ author empty$
    { key empty$
        { "to sort, need author or key in " cite$ * warning$ "" }
        { key sortify }
      if$
    }
    { author sort.format.names }
  if$
}

FUNCTION {author.title.sort}
{ author empty$
    { title empty$
        { key empty$
            { "to sort, need author, title, or key in " cite$ * warning$ "" }
            { key sortify }
          if$
        }
        { title sort.format.title }
      if$
    }
    { author sort.format.names
      "    "
      *
      title field.or.null sort.format.title
      *
    }
  if$
}

FUNCTION {presort}
{ author.title.sort
  "    "
  *
  year field.or.null sortify
  *
  "    "
  *
  title field.or.null sort.format.title
  *
  #1 entry.max$ substring$
  'sort.label :=
}

ITERATE {presort}

SORT

STRINGS { longest.label last.label next.extra }

INTEGERS { longest.label.width last.extra.num number.label }

FUNCTION {initialize.longest.label}
{ "" 'longest.label :=
  #0 int.to.chr$ 'last.label :=
  "" 'next.extra :=
  #0 'longest.label.width :=
  #0 'last.extra.num :=
  #0 'number.label :=
}

FUNCTION {forward.pass}
{ last.label author.title.sort =
    { last.extra.num #1 + 'last.extra.num :=
      last.extra.num int.to.chr$ 'extra.label :=
    }
    { "a" chr.to.int$ 'last.extra.num :=
      "" 'extra.label :=
      author.title.sort 'last.label :=
    }
  if$
  number.label #1 + 'number.label :=
}

FUNCTION {reverse.pass}
{ next.extra "b" =
    { "a" 'extra.label := }
    'skip$
  if$
  extra.label 'next.extra :=
  extra.label duplicate$ empty$
    'skip$
    { "{\natexlab{" swap$ * "}}" * }
  if$
  'extra.label :=
  label extra.label * 'label :=
}

EXECUTE {initialize.longest.label}

ITERATE {forward.pass}

REVERSE {reverse.pass}

FUNCTION {begin.bib}
{ preamble$ empty$
    'skip$
    { preamble$ write$ newline$ }
  if$
  "\begin{thebibliography}{" number.label int.to.str$ * "}" *
  write$ newline$
  "\providecommand{\natexlab}[1]{#1}"
  write$ newline$
}

EXECUTE {begin.bib}

EXECUTE {init.state.consts}

ITERATE {call.type$}

FUNCTION {end.bib}
{ newline$
  "\end{thebibliography}" write$ newline$
}

EXECUTE {end.bib}
