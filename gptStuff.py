from g4f.client import Client

import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def sendToGpt(data):
    client = Client()
    
    prompt = f"это ссылка на новостную статью, сделай из нее короткий, компактный пост для Телеграма (максимум 4 предлодения) на оригинальном языке\n{data}"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        web_search=False
    )
    
    return response.choices[0].message.content

# data = "'Title: Czołowe zderzenie i dachowanie. Za kierownicą 20‑latek, Content: 20-letni kierowca podczas manewru wyprzedzania zderzył się czołowo z nadjeżdżającym z naprzeciwka volvo. Auta wypadły z drogi i dachowały. Dwie osoby trafiły do szpitala. Do wypadku doszło 1 lutego ok. godz. 18 na drodze krajowej nr 53 między Dylewem a Kadzidłem (woj. mazowieckie). 20-letni kierowca volkswagena podczas wyprzedzania zderzył się czołowo z volvo - informuje serwis moja-ostroleka.pl. Volkswagenem jechały trzy osoby. Wszystko wskazuje na to, że nic im się nie stało. Volvo kierował 39-latek. Jechał z pasażerem. Karetka pogotowia zabrała ich do szpitala. Dalsza część artykułu pod materiałem wideo. - Kierowcy byli trzeźwi - powiedział serwisowi nadkom. Tomasz Żerański, oficer prasowy Komendy Miejskiej Policji w Ostrołęce. Na miejscu wypadku obecne były jednostki OSP Kadzidło, OSP Dylewo, PSP Ostrołęka, policja oraz zespół karetki pogotowia. Jak informuje serwis moja-ostroleka.pl, droga w miejscu zdarzenia była przez kilka godzin zablokowana, kierowcy byli kierowani na objazdy.'"
# result = sendToGpt(data)
# print(result)
