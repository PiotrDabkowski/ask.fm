import random

males=['Jakub', 'Jan', 'Mateusz', 'Bartek', 'Kacper', 'Szymon', 'Antoni', 'Filip', 'Piotr', 'Maciej', 'Aleksander', 'Adam', 'Wiktor', 'Krzysztof', 'Wojtek', 'Igor', 'Karol', 'Dawid', 'Tomasz', 'Patryk', 'Oskar', 'Dominik', 'Kamil', 'Oliwier', 'Ignacy', 'Marcel', 'Hubert', 'Adrian', 'Sebastian', 'Julian', 'Krystian', 'Marcin', 'Tymon']

females=['Julia', 'Maja', 'Zuzia', 'Aleksandra', 'Natalia', 'Wiktoria', 'Zofia', 'Oliwia', 'Maria', 'Alicja', 'Amelia', 'Lena', 'Gabriela', 'Karolina', 'Weronika', 'Martyna', 'Emilia', 'Patrycja', 'Marta', 'Nikola', 'Nina', 'Dominika', 'Helena', 'Agata', 'Laura', 'Kinga', 'Paulina', 'Klaudia', 'Michalina', 'Iga', 'Milena']

surnames=['Nowak', 'Kowalski', 'Lewandowski', 'Kowalczyk', 'Jankowski', 'Wojciechowski', 'Kwiatkowski', 'Kaczmarek', 'Mazur', 'Krawczyk', 'Piotrowski', 'Grabowski', 'Nowakowski', 'Michalski', 'Nowicki', 'Adamczyk', 'Dudek', 'Wieczorek', 'Majewski', 'Olszewski', 'Jaworski', 'Malinowski', 'Pawlak', 'Witkowski', 'Walczak', 'Rutkowski', 'Michalak', 'Sikora', 'Ostrowski', 'Baran', 'Duda', 'Szewczyk', 'Tomaszewski', 'Pietrzak', 'Marciniak', 'Zalewski', 'Jakubowski', 'Zawadzki', 'Sadowski', 'Chmielewski', 'Borkowski', 'Czarnecki', 'Sawicki', 'Kubiak', 'Maciejewski', 'Kucharski', 'Wilk', 'Kalinowski', 'Mazurek', 'Wysocki', 'Adamski', 'Wasilewski', 'Sobczak', 'Andrzejewski', 'Zakrzewski', 'Sikorski', 'Krajewski', 'Gajewski', 'Szymczak', 'Szulc', 'Baranowski', 'Laskowski', 'Makowski', 'Przybylski', 'Nowacki', 'Borowski', 'Chojnacki', 'Ciesielski', 'Szczepaniak', 'Krupa', 'Kaczmarczyk', 'Kowalewski', 'Urbaniak', 'Kozak', 'Kania', 'Czajkowski', 'Mucha', 'Tomczak', 'Markowski', 'Kowalik', 'Nawrocki', 'Brzozowski', 'Janik', 'Wawrzyniak', 'Markiewicz', 'Tomczyk', 'Jarosz', 'Kurek', 'Wolski', 'Dziedzic', 'Stasiak', 'Stankiewicz', 'Urban', 'Dobrowolski', 'Pawlik', 'Kruk', 'Piasecki', 'Wierzbicki', 'Polak', 'Janicki', 'Sosnowski', 'Bednarek', 'Majchrzak', 'Bielecki', 'Sowa', 'Milewski', 'Gajda', 'Klimek', 'Olejniczak', 'Ratajczak', 'Romanowski', 'Matuszewski', 'Madej', 'Kasprzak', 'Grzelak', 'Socha', 'Czajka', 'Marek', 'Kowal', 'Bednarczyk', 'Skiba', 'Wrona', 'Owczarek', 'Marcinkowski', 'Matusiak', 'Orzechowski', 'Sobolewski', 'Kurowski', 'Rogowski', 'Olejnik', 'Mazurkiewicz', 'Czech', 'Janiszewski', 'Bednarski', 'Chrzanowski', 'Bukowski', 'Czaja', 'Lisowski', 'Grzybowski', 'Pluta', 'Morawski', 'Sobczyk', 'Augustyniak', 'Rybak', 'Marzec', 'Konieczny', 'Marczak', 'Zych', 'Michalik', 'Kaczor', 'Kubicki', 'Paluch', 'Niemiec', 'Sroka', 'Stefaniak', 'Cybulski', 'Kacprzak', 'Kasprzyk', 'Kujawa', 'Lewicki', 'Przybysz', 'Stachowiak', 'Piekarski', 'Matysiak', 'Janowski', 'Murawski', 'Cichocki', 'Witek', 'Niewiadomski', 'Staniszewski', 'Bednarz', 'Lech', 'Rudnicki', 'Kulesza', 'Turek', 'Chmiel', 'Biernacki', 'Skrzypczak', 'Karczewski', 'Drozd', 'Pietrzyk', 'Komorowski', 'Antczak', 'Banach', 'Filipiak', 'Grochowski', 'Graczyk', 'Gruszka', 'Klimczak', 'Siwek', 'Konieczna', 'Serafin', 'Bieniek', 'Godlewski', 'Kulik', 'Zawada', 'Ptak', 'Strzelecki', 'Zarzycki', 'Mielczarek', 'Bartkowiak', 'Krawiec', 'Janiak', 'Bartczak', 'Winiarski', 'Tokarski', 'Panek', 'Konopka', 'Frankowski', 'Banasiak', 'Grzyb', 'Rakowski', 'Zaremba', 'Skowron', 'Dobosz', 'Witczak', 'Nawrot', 'Sienkiewicz', 'Kostrzewa', 'Kucharczyk', 'Rybicki', 'Biernat', 'Bogusz', 'Rogalski', 'Szymczyk', 'Janus', 'Szczepanik', 'Buczek', 'Szostak', 'Kaleta', 'Kaczorowski', 'Tkaczyk', 'Grzegorczyk', 'Drzewiecki', 'Trojanowski', 'Jurek', 'Gawron', 'Wojtczak', 'Rogala', 'Kula', 'Kubik', 'Maliszewski', 'Radomski', 'Kisiel', 'Cebula', 'Rosiak', 'Grzesiak', 'Gawlik', 'Cygan', 'Rojek', 'Bogucki', 'Mikulski', 'Walkowiak', 'Malec', 'Flis', 'Czapla', 'Drozdowski', 'Rzepka', 'Pawelec', 'Lipski', 'Wnuk', 'Andrzejczak', 'Zaborowski', 'Falkowski', 'Filipek', 'Ciszewski', 'Nowaczyk', 'Bielawski', 'Krysiak', 'Hajduk', 'Lisiecki', 'Mroczek', 'Pietras', 'Karwowski', 'Lach', 'Dziuba', 'Borek', 'Krakowiak', 'Wasiak', 'Skrzypek', 'Lasota', 'Mika', 'Juszczak', 'Borowiec', 'Sobieraj', 'Dubiel', 'Dominiak', 'Kmiecik', 'Bujak', 'Kubacki', 'Pilarski', 'Gutowski', 'Misiak', 'Tarnowski', 'Bartosik', 'Mierzejewski', 'Jakubiak', 'Twardowski', 'Zielonka', 'Jezierski', 'Jurkiewicz', 'Florczak', 'Janas', 'Bilski', 'Stelmach', 'Bochenek', 'Stec', 'Staszewski', 'Dudziak', 'Noga', 'Skoczylas', 'Pasternak', 'Matuszak', 'Piwowarczyk', 'Filipowicz', 'Milczarek', 'Adamus', 'Cholewa', 'Olczak', 'Koza', 'Czechowski', 'Wilczek', 'Kaczmarski', 'Jankowiak', 'Strzelczyk', 'Kubica', 'Misztal', 'Sieradzki', 'Adamczak', 'Szwed']

def make_female_surname(surname):
   if surname[-3:] in ['ski','zki','cki']:
      return surname[0:-1]+'a'
   return surname

def get_surname(male=True):
    if male:
       return random.choice(surnames)
    return make_female_surname(random.choice(surnames))

def get_name(male=True):
    if male:
        return random.choice(males)+' '+get_surname()
    return random.choice(females)+' '+get_surname(False)

def login_from_name(name, age):
   org=name
   name=name.split(' ')
   login=''
   if 1:
      n_part=random.randrange(4)+1
      s_part=random.randrange(4)+1
      a=random.randrange(2)
      a_part=random.randrange(5)
      n_low=random.randrange(4)
      separation=random.randrange(4)
      if n_part!=4:
         login+=name[0][0:n_part]
      else:
         login+=name[0]
      if not n_low:
            login.lower()
      if not separation:
         login+=['1','2','3'][random.randrange(3)]
      if a and not a_part:
         login+=str(age)
      if s_part!=4:
         login+=name[1][0:s_part]
      else:
         login+=name[1]
      if a and a_part:
         login+=str(age)
   if len(login)<6:
      return login_from_name(org, age)
   return login

def random_str(length, symbol=False):
   a='ABCDEFGHIJKLMNOPRSTUWXYZ'
   b='abcdefghijklmnoprstuwxyz'
   c='0123456789'
   d='.!'
   s=random.choice(a)
   n=3 if symbol else 2
   while n<length:
      s+=random.choice(b)
      n+=1
   s+=random.choice(c)
   if symbol:
      s+=random.choice(d)
   return s
      
      
            
   
