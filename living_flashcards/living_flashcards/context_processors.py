from lang_selection.models import UserLanguage

def language_options(request):
    available_languages = ["English"]
    available_languages_to_learn = ["Sora", "Future language 1", "Future language 2"]
    selected_language = "Sora"
    if available_languages_to_learn:
        selected_language = available_languages_to_learn[0]

    if request.user.is_authenticated:
        try:
            user_language = UserLanguage.objects.filter(djangousermodel=request.user).first()
            if user_language and user_language.language:
                if user_language.language in available_languages_to_learn:
                    selected_language = user_language.language
                elif user_language.language in available_languages:
                    selected_language = user_language.language
        except Exception:
            pass

    return {
        "available_languages": available_languages,
        "available_languages_to_learn": available_languages_to_learn,
        "selected_language": selected_language,
    }
