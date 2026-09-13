% ICML 2025 Bibliography Style (simplified version based on plainnat)
ENTRY
  { address
    author
    booktitle
    chapter
    doi
    edition
    editor
    howpublished
    institution
    journal
    key
    month
    note
    number
    organization
    pages
    publisher
    school
    series
    title
    type
    url
    volume
    year
  }
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

FUNCTION {format.names}
{ 's :=
  #1 'nameptr :=
  s num.names$ 'numnames :=
  numnames 'namesleft :=
    { namesleft #0 > }
    { s nameptr "{ff~}{vv~}{ll}{, jj}" format.name$ 't :=
      nameptr #1 >
        { namesleft #1 >
            { ", " * t * }
            { numnames #2 >
                { "," * }
                'skip$
              if$
              t "others" =
                { " et~al." * }
                { " and " * t * }
              if$
            }
          if$
        }
        't
      if$
      nameptr #1 + 'nameptr :=
      namesleft #1 - 'namesleft :=
    }
  while$
}

INTEGERS { nameptr namesleft numnames }

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

FUNCTION {format.btitle}
{ title emphasize }

FUNCTION {format.date}
{ year empty$
    { "" }
    { year }
  if$
}

FUNCTION {format.booktitle}
{ booktitle empty$
    { "" }
    { "In " booktitle emphasize * }
  if$
}

FUNCTION {format.journal}
{ journal empty$
    { "" }
    { journal emphasize }
  if$
}

FUNCTION {format.volume}
{ volume empty$
    { "" }
    { volume }
  if$
}

FUNCTION {format.pages}
{ pages empty$
    { "" }
    { "pp. " pages * }
  if$
}

FUNCTION {article}
{ output.bibitem
  format.authors "author" output.check
  new.block
  format.title "title" output.check
  new.block
  format.journal "journal" output.check
  format.volume output
  format.date "year" output.check
  format.pages output
  new.block
  note output
  fin.entry
}

FUNCTION {inproceedings}
{ output.bibitem
  format.authors "author" output.check
  new.block
  format.title "title" output.check
  new.block
  format.booktitle "booktitle" output.check
  format.date "year" output.check
  format.pages output
  new.block
  note output
  fin.entry
}

FUNCTION {book}
{ output.bibitem
  format.authors "author" output.check
  new.block
  format.btitle "title" output.check
  new.block
  publisher "publisher" output.check
  format.date "year" output.check
  new.block
  note output
  fin.entry
}

FUNCTION {misc}
{ output.bibitem
  format.authors output
  new.block
  format.title output
  new.block
  howpublished output
  format.date output
  new.block
  note output
  fin.entry
}

FUNCTION {default.type} { misc }

FUNCTION {output.bibitem}
{ newline$
  "\bibitem{" write$
  cite$ write$
  "}" write$
  newline$
  ""
  before.all 'output.state :=
}

FUNCTION {sortify}
{ purify$
  "l" change.case$
}

FUNCTION {presort}
{ type$ "book" =
  type$ "inbook" =
  or
    'author.sort
    { type$ "proceedings" =
        'editor.sort
        'author.sort
      if$
    }
  if$
  "    "
  *
  year field.or.null sortify
  *
  "    "
  *
  title field.or.null
  sortify
  *
  #1 entry.max$ substring$
  'sort.key$ :=
}

FUNCTION {author.sort}
{ author empty$
    { key empty$
        { "to sort, need author or key in " cite$ * warning$
          ""
        }
        { key sortify }
      if$
    }
    { author sortify }
  if$
}

FUNCTION {editor.sort}
{ editor empty$
    { key empty$
        { "to sort, need editor or key in " cite$ * warning$
          ""
        }
        { key sortify }
      if$
    }
    { editor sortify }
  if$
}

READ
ITERATE {presort}
SORT
ITERATE {call.type$}
