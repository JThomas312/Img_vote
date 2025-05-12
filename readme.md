# Img_vote

**Img_vote** is an open-source python library to help you display images in a browser and ask users to add information to those images. You can view this as *tags*, *metadata*, *caracteristics* ... The original idea was to create statistically significant data for scientific studies, but you may use it however you want.

**Img_vote** displays a list of *cases*, one or several images of the same subject alongside the list of *tags*, with one or more *conclusion*.

*Tags* are sparated in 2 categories, **image caracteristics** (things users see on the images) and **case conclusions** (what users think the case represents based on all images). Some of these **conclusions** may be hidden from the user, for example if it can be derived from other conclusions, whilst remaining relevant to your statistics study, or if you want (and can) include a *"gold standard"* (i.e. the right answer, which you obviously don't want your users to have)

To use **Img_vote** you will need a little bit of configuration, namely list your *tags*, define your cases and set a duration to start your study. Once this is over you can export your *results* to a **spreadsheet** or **csv** file.

> Full disclaimer, I am not a web designer and this library was designed with practical use in mind. Whilst I would love to render it prettier, it is not amongst my top priorities.

**Img_vote** contains the following features :
- In-browser image display
- *Tag* display as yes/no answers
- On-click saving of your answers (so as not to lose your work over a single disconnection)
- Admin interface with start/pause/stop control over your *study* to lock/unlock access to the database
- File export to **.ods .xls(x) .csv** format

