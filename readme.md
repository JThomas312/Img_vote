
# Img_vote

*Img_vote* is an open-source python library to help you display images in a browser and ask users to add information to those images. You can view this as *questions*, *tags*, *metadata*, *caracteristics* ... You will be conducting **studies** where **reviewers** will answer questions you have prepared about images.

*Img_vote* displays a list of *cases*, one or several images of the same subject alongside the list of *questions*, answers to those question must be prepared beforehand.

*Tags* are separated in 3 categories, **yes/no** (list of criteria that are either present or absent), **one from several** (mutually exclusive answers) and **numerical values** (which are positive integers only).  A single **one from several** question may be used as a *"gold standard"* (i.e. the right answer) that **reviewers** will not see.

The use of *Img_vote* should be pretty straightforward, you will create a **study**, prepare questions called **categories**, upload images and then open access to your **reviewers** so they can answer the questions. Once your study is over you can export your *results* to a **spreadsheet** or **csv** file.

> AI disclaimer, AI was used to create the graphic part of the original frontend, later pages were hand designed following the same chart.

*Img_vote* contains the following features :
- In-browser image display
- *Tag* display as **yes/no**, **one from several** and **positive integer**
- On-click saving of your answers (so as not to lose your work over a single disconnection)
- Admin interface to manage your *studies* (create, write questions, upload images) and start, pause, stop to lock/unlock access to the database
- File export to **.ods** and **.xlsx** format

*Img_vote* was originally developed  for study **Validity and Reliability of Intraoperative Onychoscopic Criteria** and development was paid for by their author. While it is open source we would ask you to quote this paper if you plan on using *Img_vote* for any published research
