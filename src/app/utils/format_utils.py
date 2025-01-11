def censor_email(email: str) -> str:
    return email[:min(3, email.index('@'))] + '***' + email[email.index('@'):]

def duration_in_words(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"

    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        if seconds == 0:
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        return f"{minutes} minute{'s' if minutes > 1 else ''} {seconds}s"

    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        if minutes == 0 and seconds == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        elif seconds == 0:
            return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes > 1 else ''}"
        return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes > 1 else ''}"

    days, hours = divmod(hours, 24)
    if hours == 0 and minutes == 0 and seconds == 0:
        return f"{days} day{'s' if days > 1 else ''}"
    elif minutes == 0 and seconds == 0:
        return f"{days} day{'s' if days > 1 else ''} {hours} hour{'s' if hours > 1 else ''}"
    return f"{days} day{'s' if days > 1 else ''} {hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes > 1 else ''}"