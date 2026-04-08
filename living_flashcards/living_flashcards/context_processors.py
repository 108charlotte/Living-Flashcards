from lang_selection.models import UserLanguage

def language_options(request):
    available_languages = ["English"]
    available_languages_to_learn = ["Sora", "Future Language 1", "Future Language 2"]
    selected_language = "Sora"
    if available_languages_to_learn:
        selected_language = available_languages_to_learn[0]

    session_selected_language = request.session.get("selected_language_to_learn")
    if session_selected_language in available_languages_to_learn:
        selected_language = session_selected_language

    if request.user.is_authenticated:
        try:
            user_language = UserLanguage.objects.filter(djangousermodel=request.user).first()
            if user_language and user_language.language:
                if (
                    user_language.language in available_languages_to_learn
                    and session_selected_language not in available_languages_to_learn
                ):
                    selected_language = user_language.language
        except Exception:
            pass

    return {
        "available_languages": available_languages,
        "available_languages_to_learn": available_languages_to_learn,
        "selected_language": selected_language,
    }
