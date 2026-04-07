from nutri.domain.survey.survey import Recommandation, get_recommandation


class SurveyService:
    @staticmethod
    def get_recommandations(answers: dict[str, float]) -> list[Recommandation]:
        results = []
        for question, score in answers.items():
            reco = get_recommandation(question, score)
            if reco is not None:
                results.append(reco)
        return results
