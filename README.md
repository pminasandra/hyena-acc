# hyena-behaviour-classifier-inator
This repo contains code for predicting hyena behaviour from accelerometer data.
The raw data used here was obtained as part of the [CCAS](https://movecall.group)
project. This project is described in detail in our [pre-print](https://www.biorxiv.org/content/10.1101/2023.05.31.543053v1.article-metrics).
The members who contributed to the code in this repo are:
- Pranav Minasandra
- Ariana Strandburg-Peshkin

The folks who worked on this project directly at other parts, including but not limited
to fieldwork, data preprocessing, etc. include:
- Frants Jensen
- Andrew Gersick
- Kay Holekamp
- Eli Strauss


# Usage
NOTE: This software was written in and for Linux terminals running the bash
shell. While there should not be any *major* issues in running the software on
Windows or Mac or other systems, you will probably have to make some minor
changes. For instance, the Windows system uses the '\' character for file
separation. While this convention is undeniably idiotic, it is also true that
Windows is a ubiquitous software, which makes it necessary for me to add these
notes. I also use bash escape characters (preceded by `'\033['`) in the code to
make displays colourful for easy readability. These will probably need to be
removed in the Windows and Mac instances of running this pipeline. 

This software was written to analyse spotted hyena accelerometry data from
collarred hyenas. It constructs an elegant machine learning system using
pre-recorded ground truth data, and provides a second-by-second (to be accurate,
three second - by - three second) report of the behavioural states of the
hyenas. This software, and all libraries used by it, are open source. 

The file [DOCS.md](./DOCS.md) provides details about how to set up and run this software
effectively and how to interpret the results. 


# Contact
If you have any questions or problems with the code, please feel free to contact
me using the methods mentioned on my website, pminasandra.github.io . If your
question is related explicitly to the code, mentioning the make and build of
your OS, and a detailed log of your error, would be very helpful. Have fun with
your analyses!

