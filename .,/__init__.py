'''__init__.py file for CincoMinutos'''

'''INTRODUCTION
    Hello to the person who is looking at my code right now. As I am not 
    a seasoned expert in Python PEPs, you might encounter weird coding
    practices and conventions as you go through the code. Some lines 
    might be too long, others might not be coded in the way you'd 
    expect. Bear with me. For easier understanding, I have outlined the
    structure of my code below.


    ORGANIZATION
    I put 1 or 2 letter "prefixes" with an underscore after it to organize
    my variables and functions. In Tkinter, a myraid of callback functions
    and dictionaries with Tkinter objects, it helps to understand the
    which method belongs in which dialog.

    m_ = main -> main dialog
    c_ = conjugation -> Simple Conjugator dialog
    s_ = settings -> Settings dialog
    t_ = testing -> Verb Check (VC) dialog
    t_t_ = testing-testing -> body of VC dialog - also shows mistakes
    t_m_ = testing-main -> entry point of VC dialog
    t_r_ = testing-review -> end point of VC dialog - shows score
    a_ = accent -> frame for accent buttons
    f_ = ScrollFrame -> frame itself and all widgets under frame
    f_c_ = ScrollFrame-conjugation
    f_t_ = ScrollFrame-testing
    f_s_ = ScrollFrame-scope


    OBJECT STORING
    There is a lot of Tkinter objects to be stored in lists. Because of
    the multiple dialogs, there is a lot of gridding an grid_forgetting
    to be done. Thus, all the objects of a dialog are stored in a handy
    list so it can be called and all the objects will be grid_forgotten
    in an iterator. The list looks like this - c_obj / s_obj /
    m_obj / t_obj
    A special case is t_obj, which is a dict for the many sub-dialogs.


    PARTIALS
    You will see that I use a lot of partials to bind objects. I don't 
    use lambdas because lambdas get called after the iterator ends, so 
    if - for i in range(10): - and I do lambdas with var numbers here, 
    lambda with i will simply become 9 all the time. Partials are awesome.
    They get around that. You can read more on partial documentation
    online.

    Coded by Markus Zhang.'''

print("__init__ file called.")