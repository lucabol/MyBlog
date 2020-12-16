---
title: Recursively extracting nested links from a webpage using Racket
date: 2020-05-11
author: lucabol
layout: post
tags:
  - racket
  - functional programming
---
  This is my first attempt at writing Racket or LISP code. It might be ugly ...
  For now, let's build a web crawler, next, I shall write myself a language.
  That's where Racket really shine.

  The code is [here](https://github.com/lucabol/website-links). Thanks to [Mike](https://github.com/mjrousos) for reviewing it.

  ## Why
  I want to translate a website, including recursively reached pages, to a pdf to read on my e-reader.
  This program does the first step: going from a URL to a list of URLs by recursively navigating the links
  on the page.

  The `PS1Script` directory contains scripts to perfrom the other steps:
  1. Translate all the links to PDF pages (using Chrome headless).
  2. Combine all the PDFs to a single document (using `cpdf`).

  ## Prelude

  First you declare which language you are using. Racket is a language to build
  languages and the language itself is just one of many (try rereading this phrase).

~~~~racket
#lang racket
~~~~

  We then expose the main functions of the library. Aka recursively getting all links from a webpage
  to a certain nesting level both as a Racket list and as a newline delimitated string.

~~~~racket
; Provides functions to extract links from web pages recursively

(provide
 ; uriString nestingLevels -> list of uriStrings
 ; Doesn't follow links to non-html resources or pointing to a different domain then uriString.
 uri->nestedLinks
 ; uriSTring nestingLevels -> string of newline separated Uri Strings
 uri->nestedLinksNl)
~~~~

  ## Implementation

  This is similar, but not identical, to C# `using` statement as you declare which packages are needed.

~~~~racket
(require (planet neil/html-parsing:2:0)
         net/url
         xml
         html
         sxml/sxpath
         threading)
~~~~

  The program crawl just links to html files in the same domain as the first URI given to it. It is
  possible to extend this more by having the program take a regular expression (or * expression) to 
  identify which file sto leave out of the crawling.

~~~~racket
(define invalid-suffixes
  '("./" ".xml" ".jpg" ".jpeg" ".png" ".gif" ".tiff" ".psd"
    ".eps" ".ai" ".indd" ".raw" ".svg"))

(define invalid-prefixes '("#" "mailto:" "javascript:"))

(define (different-domain? baseUrl l)
  (define url (string->url l))
  (and (url-host url) (not (equal? (url-host baseUrl) (url-host url)))))

(define (good-link? baseUrl l) (not (or (different-domain? baseUrl l)
                                (ormap (curry string-suffix? l) invalid-suffixes)
                                (ormap (curry string-prefix? l) invalid-prefixes))))
~~~~

  Next we have to parse the HTML. We use XPath for that. Racket is particularly good for XML parsing as
  it maps naturally to expressions which are the bread and butter of the language. I don't enjoy
  the nesting of expressions that LISP like languages force onto you (as in the expression below). But
  see later for a partial solution.

~~~~racket
(define (xexp->links xexp) (flatten (map cdr ((sxpath "//a/@href") xexp))))
~~~~

  The strange `~>>` operator in the code below comes from the [`Threading`](https://docs.racket-lang.org/threading/index.html)
  package. This set of macros lets you build pipelines of computations similarly to the F# `|>` operator.
  The initial value comes first and then the functions are applied in series each one to the result of 
  the previous. By doing that you 'flatten' the nested expressions, making them more readable (at least to my eyes).

  This capability of changing the core behavior of the language is something very peculiar to the LISP family,
  and the reaason why I am attracted to Racket in the first place.

  This function extracts all the 'good' links from a url. BTW: I love that you can use `->` to name symbols.

~~~~racket
(define (url->links url)
  (~>> (call/input-url url get-pure-port html->xexp)
       xexp->links
       (filter (curry good-link? url))))
~~~~

 λ~> is the function composition operator in the 'Threading' library. You got to love embedding lambdas in the code. 

~~~~racket
(define uri->links
  (λ~> string->url url->links))
~~~~

  This is the main recursive workhorse of the program. It works something like this (numbers marked in the code):

  0. Treat links to subparts of a web page as if they were links to the webpage
  1. If it is not a good link, return the links already visited (`visited`)
  2. Same thing if the link is alread in `visited`
  3. If we reached the nesting level specified, add the link to `visited` and return 'visited'
  4. Otherwise add the link to `visited` and call yourself on all sublinks on the page

  The function is not tail recursive, but that is not a huge deal in Racket as the stack is very large.
  It doesn't blow up as easily as in most other languages.

~~~~racket
(define (uri->nestedLinks-rec baseUrl uri visited levels)
  
  (define abs-url (if (string-contains? uri "#") ; <0>
      (~> uri (string-split "#") first (combine-url/relative baseUrl _))
      (~>> uri (combine-url/relative baseUrl))))
  
  (log-info "~a, ~a, ~a:~a~n" (url->string baseUrl)
                              levels uri (url->string abs-url))

  (cond [(not (good-link? baseUrl uri)) visited] ; <1>
        [(member abs-url visited)  visited]      ; <2>
        [(zero? levels)  (cons abs-url visited)] ; <3>
        [else  (for/fold ([acc (cons abs-url visited)]) ;<4>
                         ([l (in-list (url->links abs-url))])
                 (uri->nestedLinks-rec abs-url l acc (sub1 levels)))]))
~~~~

 Finally we can trivially define the two main functions in the module. 

~~~~racket
(define (uri->nestedLinks uri levels)
  (reverse (uri->nestedLinks-rec (string->url uri) "" '() levels)))

(define (uri->nestedLinksNl uri levels)
  (define links (uri->nestedLinks uri levels))
  (string-join (map url->string links) "\n" #:after-last "\n"))
~~~~

## Test
To my great pleasure, Racket allows (encourages?) you to have tests in the same file as the code.
They just go into sub modules, that can be constructed piecewise with the `module+` instruction.

You could add the tests beside each function, but I decided to have a separate section in the file
instead. To run them you call `raco test FILENAME`.

~~~~racket
(define (uri->path test-uri)
        (build-path "./data" (~> test-uri first uri->file string->path)))
(define uri->file (λ~> string->url url-host))
(define test-uris '(
                    ("https://www.lucabol.com" 3)
                    ("https://beautifulracket.com/" 3)
                    ("https://en.wikipedia.org/wiki/Typeface" 1)
                    ("https://brieferhistoryoftime.com" 3)
                    ("https://mobydick.wales/" 3)
                    ("https://resilientwebdesign.com" 3)
                    ("https://www.c82.net/euclid/" 3)
                    ))

(module+ test
  (require rackunit)
~~~~

 I got a bit sloppy not naming my lambdas here ... But, doesn't the lambda symbol look cool? 

~~~~racket
  (for-each (λ (test-uri)
              (with-input-from-file
                  (uri->path test-uri)
                (λ () (begin
                        (define saved-result (port->string))
                        (define calc-result
                          (uri->nestedLinksNl (first test-uri) (second test-uri)))
                        (check-equal? calc-result saved-result test-uri)))
                #:mode 'text
                ))
            test-uris))
~~~~

 This is used to regenerate the test data. You can then inspect it manually before running tests. 

~~~~racket
(define (refresh-test-data)
    (for-each (λ (test-uri)
                (with-output-to-file
                    (uri->path test-uri)                  
                  (λ () (display (uri->nestedLinksNl (first test-uri) (second test-uri))))
                  #:exists 'replace))
              test-uris))
~~~~

  ## Main

  Main goes into its own submodule as well. Racket is not as pure as Haskell, so you can naturally 
  manage side effects like user input and such. You got to appreciate the concisivness of the command
  line parsing library.

  The code below looks a bit odd to me. It could probably be refactored
  so that the parser expression returns the values instead of filling out  parameters.

~~~~racket
(module+ main

  (define levels (make-parameter "3"))
  (define uri (make-parameter #f))

  (define parser
    (command-line
     #:program "website-links"
     #:usage-help "Extracts links from a webpage recursively to a specified level."
     #:once-each
     [("-l" "--levels") LEVELS "How many nested levels to process (default 3)." (levels LEVELS)]
     #:args (URI) (uri URI)))
      
  (display (uri->nestedLinksNl (uri) (string->number (levels)))))
  
~~~~

  ## Conclusion

  I liked Racket very much. It takes a little while to get use to the expression syntax, which is very
  different from the C-like one most of us are used to. It also takes a while to get used to the style 
  of the documentation, which is written very precisely for the careful reader. We are more used to the
  'here is an example, copy it' kind of documentation. For the distracted programmer ...
  
