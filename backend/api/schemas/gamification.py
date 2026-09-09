from pydantic import BaseModel


class AchievementOut(BaseModel):
    code: str
    title: str
    description: str
    unlocked_at: str


class GamificationStateOut(BaseModel):
    xp_total: int
    level: int
    xp_into_level: int
    xp_for_next_level: int
    streak_days: int
    achievements: list[AchievementOut]
