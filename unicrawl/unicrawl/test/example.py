txt = """Chia sẻ:\n ](https://www.\nfacebook.\ncom/sharer/sharer.\nphp?u=http://en.\nhvnh.\nedu.\nvn/hvnhta/en/news/the-\nhandover-and-inauguration-ceremony-of-bav-mb-digital-hub-in-banking-academy-\nof-vietnam-437.\nhtml "Chia sẻ facebook")\n ](https://twitter.\ncom/share?url=http://en.\nhvnh.\nedu.\nvn/hvnhta/en/news/the-\nhandover-and-inauguration-ceremony-of-bav-mb-digital-hub-in-banking-academy-\nof-vietnam-437.\nhtml "Chia sẻ twitter")\n \n \n\n* * *\n\n### The Handover and Inauguration Ceremony of BAV – MB Digital Hub in Banking\nAcademy of Vietnam\n\n_Date: 20/12/2021_\n\nOn November 18th, 2021, at the Banking Academy of Vietnam, the Handover and\nInauguration Ceremony of Digital Creative Space (BAV - MB Digital Hub) was\ntaken place according to the cooperation agreement signed between the Banking\nAcademy of Vietnam (BAV) and the Military Commercial Joint Stock Bank (MB).\n\n\nAttending the ceremony, the representative of MB included Mr.\n Luu Trung Thai,\nVice Chairman of the Board of Directors and General Director (General\nDirector); Ms.\n Tran Thi Bao Que and Mr.\n Vu Thanh Trung, Member of the Board of\nManagement; Mr.\n Chu Hai Cong, Chief of Office of the CEO; Ms.\n Dang Minh Huyen,\nDirector of Human Resources; and Mr.\n Nguyen Viet Chau, Director of Innovation\nLab.\n\n\nOn the side of BAV, there was Assoc.\nProf.\nDr.\n Do Thi Kim Hao – Vice President\nin charge of the President of BAV, Assoc.\nProf.\nDr.\n Le Van Luyen, Assoc.\nProf.\nDr.\n\nMai Thanh Que – Vice President and several leaders of departments in BAV.\n\n\nAt the Ceremony, Assoc.\nProf.\nDr.\n Do Thi Kim Hao – Vice President in charge of\nthe President of BAV, said that one of the new points in the training programs\nin BAV is to develop digital competence for students in all subjects."""
import re

pattern = r"(?P<url>https?://[^\s]+)"

matches = re.finditer(pattern, txt, re.MULTILINE)

for matchNum, match in enumerate(matches, start=1):
    print(match.start(), match.end())
    s = match.start()
    e = match.end()
    print(txt[s:e])
