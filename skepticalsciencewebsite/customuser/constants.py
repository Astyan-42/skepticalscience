# default score

SKEPTIC_SCORE_DEFAULT = 5.0
MEAN_PUBLICATION_SCORE_DEFAULT = 5.0
MEAN_IMPACT_FACTOR_DEFAULT = 100.0
ESTIMATOR_SCORE_DEFAULT = 0.5
REVIEWER_SCORE_DEFAULT = 0.5

# max score

SKEPTIC_SCORE_MAX = 10.0
MEAN_PUBLICATION_SCORE_MAX = 10.0
MEAN_IMPACT_FACTOR_MAX = 1000.0
ESTIMATOR_SCORE_MAX = 1.0
REVIEWER_SCORE_MAX = 1.0

# normalize computation

SKEPTIC_SCORE_NORMALIZE = lambda score: (score or SKEPTIC_SCORE_DEFAULT)/SKEPTIC_SCORE_MAX
MEAN_PUBLICATION_SCORE_NORMALIZE = lambda score: (score or MEAN_PUBLICATION_SCORE_DEFAULT)/MEAN_PUBLICATION_SCORE_MAX


def MEAN_IMPACT_FACTOR_NORMALIZE(score):
    score = (score or MEAN_IMPACT_FACTOR_DEFAULT)
    score = 1.35074 + (1.041878e-16 - 1.35074)/(1 + (score/217.0499)**0.6858419)
    return score


ESTIMATOR_SCORE_NORMALIZE = lambda score: (score or ESTIMATOR_SCORE_DEFAULT)/ESTIMATOR_SCORE_MAX
REVIEWER_SCORE_NORMALIZE = lambda score: (score or REVIEWER_SCORE_DEFAULT)/REVIEWER_SCORE_MAX
