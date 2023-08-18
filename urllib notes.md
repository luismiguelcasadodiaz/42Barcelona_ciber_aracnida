# My notes about RFC

IETF - Internet Engineering Task Force, founded in 1986, is the premier standards development organization (SDO) for internet.

The RFC (Request for comments) produced by the IETFS cover many aspects of computer networking.

The RFC series has two sub-series, STDs and BCPs, with each numbered STD and BCP comprising one or more RFCs. 

STDs are **Internet Standard**  RFCs and BCPs are RFCs that describe **Best Current Practices in the Internet, some of which are administrative processes for the IETF.

Only some RFCs are standards.

The canonical place to find RFCs is the [RFC Editor Web Site](https://rfc-editor.org/)
Some key information is missing there, so most people use [tools.ietf.org](https://tools.ietf.org/)
Plain text RFCs are difficult to read bordering and ugly.
For more usable RFCs, you can use third-party repositories [greenbytes](https://greenbytes.de/tech/webdav/)
keeps a list of WebDAV-related RFCs, and the[HTTP Working Group](https://httpwg.org/specs/) maintains a selection of those related to HTTP.

# Is it current?
The ASCII text RFCs (e.g., at the RFC Editor site) don't tell you what documents update or obsolete the document you are currently looking at.

[Errata search](https://www.rfc-editor.org/errata_search.php)

[Check differences}(htps://author-tools.ietf.org/iddiff)

# Understanding context
It is necessary to read not only the directly relevant text but also (at a minimum) anything that it references, whether that is in the same spec or a different one. In a pinch, reading any potentially related sections will help immensely, if you can not read the whole document.

Many protocols set up [IANA registries](https://www.iana.org/protocols) to manage their extension points; These, not the specifications, are the sources of truth. For example, the canonical list of HTTP methods is in [this registry](https://www.iana.org/assignments/http-methods/http-methods.xhtml), not any of the HTTP specifications.


Another very common pitfall is to skim the specification for examples and implement what they do. Examples typically get the least amount of attention from authors. They are very often the least reliable parts of the spec.

# Python's urllib.request for HTTP Requests

\pard\pardeftab720\partightenfactor0

\f0\b0\fs24 \cf5 \strokec5 \
\
Desde {\field{\*\fldinst{HYPERLINK "https://realpython.com/urllib-request/"}}{\fldrslt https://realpython.com/urllib-request/}}\
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0
\cf0 \cb1 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 Requests is not a built-in library\
Use url lib.request to stick to standard-library.\
\pard\pardeftab720\partightenfactor0

\f3 \cf7 \cb4 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec7 \'a0{\field{\*\fldinst{HYPERLINK "https://datatracker.ietf.org/doc/html/rfc7230"}}{\fldrslt \cf8 \strokec8 RFC 7230, part 1: Message Syntax and Routing}},\
Tras entender los RFC\'85. La ultima version June 2022 de la especificaci\'f3n es la 9112 conocida tambien como std99\
\
\
The target of an HTTP request is called a \'93Resource. Each resource is identified by a URI: Uniform Resource Identifier.\
A) URL is the most common URI\
\
{\field{\*\fldinst{HYPERLINK "https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages"}}{\fldrslt HTTP Messages}}\
\pard\pardeftab720\partightenfactor0

\fs32 \cf9 \strokec9 HTTP messages are how data is exchanged between a server and a client.\
Requests\
Responses\
HTTP/1.1 open text\
HTTP/2 Binary Framing\
\
Requests and responses has similar structure\
\pard\tx220\tx720\pardeftab720\li720\fi-720\partightenfactor0
\ls1\ilvl0\cf9 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8259 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec9 Start-line: SINGLE LINE. Request description or response status.\
\ls1\ilvl0\kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8259 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec9 Set of headers\
\ls1\ilvl0\kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8259 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec9 Empty blank lines\
\ls1\ilvl0\kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8259 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec9 Body}
