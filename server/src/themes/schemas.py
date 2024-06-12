from schemas_config import MyBaseModel
from sections.schemas import SectionRead


class ThemeRead(MyBaseModel):
    id: int
    title: str
    section: SectionRead
