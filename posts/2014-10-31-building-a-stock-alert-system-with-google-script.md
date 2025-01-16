---
id: 268
title: Building a stock alert system with Google Script
date: 2014-10-31T08:11:13+00:00
author: lucabol
layout: post
guid: http://lucabolognese.wordpress.com/?p=268
sharing_disabled:
  - "1"
geo_public:
  - "0"
description: "Who needs fancy trading platforms when you've got Google Sheets and a dream? Watch as we build a DIY stock alert system using nothing but Google Script and Yahoo's API. A tale of spreadsheet wizardry, web scraping, and the occasional timeout error that keeps us humble"
categories:
  - Investing
  - javascript
tags:
  - Financial
---
&nbsp;


***This is obsolete as Yahoo stopped their quote service. I have a new spreadsheet [here](https://docs.google.com/spreadsheets/d/1OimxgxAgwY3GeCSvnzlEbQTPnWDU0-AnyvZMc3RfgdA/edit?usp=sharing).***

When I thought about it, I realized that my ideal system would be a spreadsheet where to add tickers and alert levels. Under the covers, the system would need to check the current price of a ticker, compare it with the alert level and send me email when triggered.

Also the whole thing shouldn't be running from my machine at home, but from somewhere on the internet.

Google script fit the bill. Let's see how it works.

Script is here. Sheet is here.

First a utility function to send errors via email, which will be used throughout the script.

~~~javascript
function emailError(e) {
  MailApp.sendEmail("lucabolg@gmail.com", "Watchlist Error",
                    "\r\nMessage: " + e.message
                    + "\r\nFile: " + e.fileName
                    + "\r\nLine: " + e.lineNumber
                    + "\r\nLOg: " + Logger.getLog())
}
~~~
Then another one to check if the price downloaded from the internet is sensible.

~~~javascript
function validPrice(price) {
 return price != 'undefined' && price > 0.1
}
~~~
We then need one to retrieve the current price of a ticker from the array of data returned from the internet:

~~~javascript
// Find the current price of a ticker in an array of data where the ticker is the first column
function getQuote(data, ticker) {
  var ticker = ticker.trim().toLowerCase()

  for(var i = 0; i = 22 && hour <= 23) || value != "close"
}
~~~
With all of that in place, we can now look at the main function. First we load up the spreadsheet and get the values and headers we care about. This would be more robust if we looked up the sheet by name. Also the id of the sheet is burned in the code. You'll need to change it if you want to make it point to your own.

~~~javascript
// Check spreadsheet with tickers and stop prices, send email when a stop is hit and mark the row as 'Executed'.
function checkQuotes() {
 try {

 // Get all data from spreadsheet in one web call.
 var ss = SpreadsheetApp.openById("1WQf2AiBPQW5HLzCyGgsFlKN0f1HTOWAteJ5bJCXVnlc")
 var range = ss.getSheets()[0].getDataRange()
 var values = range.getValues()
 var headers = values[0]
 var rows = ObjApp.rangeToObjects(values)
 var body = ""
 var now = new Date()
~~~
Notice 'ObjApp' is part of the ObjService library to make the code a bit more maintainable, instead of scattering column numbers in the code.

Now we get all the tickers and download the prices from Yahoo (we try three times as it occasionally fails.

~~~javascript
    // Fish out all tickers from col 0 where Status (col 4) is not executed
    var tickers = []
    for(var i = 1; i < rows.length; i++) {// dont' process the headers
      if((rows[i]).executed.toLowerCase() == 'active' && isRightTime(rows[i], now)) tickers.push((rows[i]).ticker.trim().toLowerCase())
    }
    Logger.log("Tickers:%s" ,tickers)

    if(tickers.length == 0) return // Nothing to process

    // Get ticker, real time bid, real time ask for all tickers in one web call
    var url = "http://finance.yahoo.com/d/quotes.csv?s=" + tickers.join("+") + "&f=sl1"//"&f=sb2b3"

    // Try 3 times before giving up
    for(var i = 0; i < 3; i++) {
      try {
        var response = UrlFetchApp.fetch(url)
        break;
      } catch(e) {
      }
    }

    Logger.log("Response:\n%s", response)
    var data = Utilities.parseCsv(response.getContentText())
    Logger.log("Data:\n%s", data)
~~~
Once that is done, we enter the main loop. The concept is simple, for each row we check the price and, if the price is above/below the alert we add it to the body string and mark the row in the sheet so that we don't process it again next time. A the end, we email the body variable if not null.

First we check that we haven't already executed this row:

~~~javascript
    for(var i = 1; i < rows.length; i++) {// dont' process the headers
      var current = rows[i]
      if(current.executed.trim().toLowerCase() == 'executed') continue // no need to process it as it is 'Executed'

      var symbol = current.operator
      var stop = current.stop
~~~
If it's still active and if it is the right time, we check if the alert is triggered. If it is we add the text to the body variable.

~~~javascript
      if(isRightTime(current, now)) {
        var price = getQuote(data, current.ticker)
        if( (symbol.trim() == ">" && price > stop) ||
           (symbol.trim() == "<" && price < stop)) {

          current.executed = "Executed"
          current.price = price

          body += [current.kind, current.ticker, current.price, current.operator, current.stop, "\r\n"].join(" ")
          Logger.log("Body in loop:\n%s", body)
        }
      }
    }
~~~
If body is not empty, that means that something was triggered, so we send the email.

~~~javascript
    if(body != "") {
      Logger.log("Body final:%s", body)
      MailApp.sendEmail('lucabolg@gmail.com', 'Watchlist: stops triggered', body)
      var data = ObjApp.objectToArray(headers, rows)
      data.unshift(headers)
      range.setValues(data)
    }
~~~
If an error was generated, then we send the error email.

~~~javascript
  } catch (e) {
    Logger.log(e.lineNumber + ":" + e.message)
    emailError(e)
  }
}
~~~
My experience overall was remarkable. The learning curve was very quick and the web editor works remarkably well (well, stepping through code is rather slow).

Overall, if Google has all your data (in Drive) and you can write code to manipulate it (in Google script), why do I need my home computer again? I can just have a small screen that connects to the internet and I'm done.

That's probably true for me apart from two things that I haven't found in web form: editing of images in the raw format and a sophisticated portfolio application. If I find these two, I'm ready to give up my life to Google ...
