# Tietokantasovellus

Kansio HY:n kurssille Tietokantasovellus.  
Kurssin itsenäinen suoritus.  


## Ohjelman määrittely

Ohjelma on perinteinen keskustelusovellus, johon käyttäjä voi luoda oman käyttäjän ja:

- Luoda keskustelualueen
- Kommentoida olevassaolevalle keskustelualueelle
- Poistaa omia viestejäsi jälkeenpäin
- Hakea omia tai muiden kirjoittamia viestejä eri keskustelualueilta
- Ylläpitäjä-oikeuksilla olevat käyttäjät voivat luoda salaisia keskustelualueita


## Ohjeet ohjelman käynnistämiseen

Klikkaa linkistä: [https://tietokantasovellus-saraste.fly.dev/](https://tietokantasovellus-saraste.fly.dev/), päästäksesi sivulle jossa sovellus ylläpidetään.

### Käynnistäminen paikallisesti:

Määritä ympäristömuuttuja `DATABASE_URL` osoittamaan PostgreSQL-tietokantaasi.

**Huom!** Sovellus on kehitetty käyttäen PostgreSQL 12.15 -versiota. 

Käynnistä sovellus Flask-kirjastolla `flask run`, ja navigoi ohjattuun osoitteeseen esim. nettiselaimella.

