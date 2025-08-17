# Gridlock Commands

All commands can be accessed via the front end `gridlock`. Apart from
`gridlock new`, be sure to set up the code and install prerequisites
as per the README before starting.

```
$ gridlock -h
gridlock - convert PDF code printouts to text

Available sub-commands

gridlock new - create new project directory
gridlock split - split PDF file to images
gridlock crop - crop page images to include only useful text
gridlock straighten - remove skew from page images
gridlock segment - find the best grid that matches page images
gridlock templates - create templates from segmented pages
gridlock text - use a LLM to get text from a page image
gridlock merge - combine the template and text
gridlock collect - assemble merged pages into a single file
```

## gridlock new

```
gridlock new PROJECT
```

Creates a new directory `PROJECT` to hold working files.

Copies in the following files from the program dir so they can be
edited on a per project basis

- `gridlock.env`
- `config.yaml`
- `prompt.md`

Add your PDF and the page number range to `config.yaml`. Set a prefix
there, which is used to identify files from the job, eg `ABC`.

## gridlock split

```
gridlock split [-f]
```

Splits the PDF into PNG image files, one per page, to the `split/`
directory.

Look at the images and find a good top left/bottom right crop point
that applies to each page, eg to remove perforations. Update `config.yaml`.

## gridlock crop

```
gridlock crop [-f] [PAGE-KEY]
```

Crops the files in `split/` based on the crop information in the
config file and store in `cropped`.

Normally invoke with no arguments and it will do all pages in
parallel. If you just want to do one page, provide `PAGE_KEY`.

`PAGE_KEY` is a reference to a page in the collection provided by
`gridlock split`. It consists of the prefix and the page number, eg
`ABC-001`.

Once an output file has been created, if you run the same command
again gridlock will not overwrite the output unless you supply the `-f`
switch; this prevents any hand edits being overwritten.

## gridlock straighten

```
gridlock straighten [-f] PAGE_KEY
```

Straighten the files from `cropped/d` using `deskew` and store in `pages/`.

## gridlock segment

```
gridlock segment [-f]
```

Looks at files in `pages/` and tries to work out the best grid
dimensions and offsets for each files. Stores output in `PREFIX.json`
in the working directory.

## gridlock templates

```
gridlock templates [-f] PAGE_KEY
```

Takes the info from `PREFIX.json` and creates two things: a) a set of
images in `grids/` showing where the grid has been placed and which
cells are non whitespace b) a set of template text files in
`templates/`.

## gridlock text

```
gridlock text [-d] [-f] PAGE_KEY
```

Calls the LLM/OCR service with each image in `pages/`, tries to extract
text and store in `text/`.

`-d` will give more debug info, such as the cost in tokens for the call.

## gridlock merge

```
gridlock merge [-d] [-f] PAGE_KEY
```

Takes the template and text and tries to merge them to `merged/`. If
it can't, will not write a file; run with `-d` to see a row/column
diff which you can use to correct files in either `text/` or
`templates/`.

## gridlock collect

```
gridlock collect [-f]
```

If all pages were merged successfully, concatenate them together to
form the file `PREFIX.txt` in the working directory.
