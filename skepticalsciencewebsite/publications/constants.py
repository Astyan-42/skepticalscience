# nb of reviewer
NB_REVIEWER_PER_ARTICLE = 4

# possible status of the publication
WAITING_PAYMENT = 1
ADDING_PEER = 2
PEER_REVIEW = 3
CORRECTION = 4
ABORTED = 5
VALIDATION = 6
EVALUATION = 7
PUBLISHED = 8

PUBLICATION_STATUS = [(WAITING_PAYMENT, "Waiting payment"),
                      (ADDING_PEER, "Adding peer"),
                      (PEER_REVIEW, "Peer review"), # no change of reviewer
                      (CORRECTION, "Correction"), # no change of reviewer
                      (ABORTED, "Aborted"),
                      (VALIDATION, "Validation"), # no change of reviewer
                      (EVALUATION, "Evaluation"),
                      (PUBLISHED, "Published")]

# seriousness of a bias
MINOR = 1
MAJOR = 2
CRITICAL = 3

SERIOUSNESS_STATUS = [(MINOR, "Minor"),
                      (MAJOR, "Major"),
                      (CRITICAL, "Critical")]

# validation status of a comment
VALIDATE = 1
IN_PROGRESS = 2
DISMISS = 3

VALIDATION_STATUS = [(VALIDATE, "Validate"),
                     (IN_PROGRESS, "In progress"),
                     (DISMISS, "Dismiss")]

# subject of a comment
FORM = 1
CONTENT = 2

COMMENT_ON = [(FORM, "Form"),
              (CONTENT, "Content")]

CONSTANTS_TEMPLATE = {
    "WAITING_PAYMENT": WAITING_PAYMENT,
    "ADDING_PEER": ADDING_PEER,
    "PEER_REVIEW": PEER_REVIEW,
    "CORRECTION": CORRECTION,
    "ABORTED": ABORTED,
    "VALIDATION": VALIDATION,
    "EVALUATION": EVALUATION,
    "PUBLISHED": PUBLISHED,
    "MINOR": MINOR,
    "MAJOR": MAJOR,
    "CRITICAL": CRITICAL,
    "VALIDATE": VALIDATE,
    "IN_PROGRESS": IN_PROGRESS,
    "DISMISS": DISMISS,
    "FORM": FORM,
    "CONTENT": CONTENT,
    "NB_REVIEWER_PER_ARTICLE" : NB_REVIEWER_PER_ARTICLE
}