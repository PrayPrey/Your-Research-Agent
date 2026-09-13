% ICML 2025 Bibliography Style (Based on plainnat)
% Simplified version for compatibility

ENTRY
  { author
    title
    journal
    year
    volume
    number
    pages
    booktitle
    publisher
    address
    note
    url
    doi
  }
  {}
  { label }

STRINGS { s t }

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

FUNCTION {output.nonnull}
{ 's :=
  output.state #0 =
    { s }
    { ", " * s * }
  if$
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

INTEGERS { output.state }

FUNCTION {init.state.consts}
{ #0 'output.state :=
}

FUNCTION {format.names}
{ 's :=
  s #1 "{ff~}{vv~}{ll}{, jj}" format.name$
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
    { title }
  if$
}

FUNCTION {format.date}
{ year empty$
    { "" }
    { year }
  if$
}

FUNCTION {format.btitle}
{ title emphasize
}

FUNCTION {format.journal}
{ journal emphasize
}

FUNCTION {article}
{ output.bibitem
  format.authors output
  format.date output
  format.title output
  format.journal output
  volume output
  pages output
  note output
  fin.entry
}

FUNCTION {inproceedings}
{ output.bibitem
  format.authors output
  format.date output
  format.title output
  "In " booktitle * output
  pages output
  note output
  fin.entry
}

FUNCTION {book}
{ output.bibitem
  format.authors output
  format.date output
  format.btitle output
  publisher output
  note output
  fin.entry
}

FUNCTION {misc}
{ output.bibitem
  format.authors output
  format.date output
  format.title output
  note output
  fin.entry
}

FUNCTION {default.type} { misc }

READ

FUNCTION {sortify}
{ purify$
  "l" change.case$
}

ITERATE {presort}

SORT

FUNCTION {begin.bib}
{ "\begin{thebibliography}{99}" write$ newline$
}

FUNCTION {end.bib}
{ newline$
  "\end{thebibliography}" write$ newline$
}

EXECUTE {begin.bib}

ITERATE {call.type$}

EXECUTE {end.bib}
