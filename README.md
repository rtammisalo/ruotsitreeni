# Tsoha - Ruotsitreeni

Sovelluksen tarkoituksena on ruotsin kielen perussanaston harjoittelu. Toisin kuin esimerkkisovelluksessa, Ruotsitreenissä ei käyttäjä voi luoda uusia harjoituksia ja/tai pakkoja, vaan kaikki harjoitukset ja sanat lisätään valmiina adminin toimesta sovelluksen tietokantaan. Pelkän suomi/ruotsi 'kortin' sijaan käytetään sovelluksessa hyödyksi kuvia, esim. kuva omenasta, jonka käyttäjä joutuu yhdistämään ruotsin kieliseen sanaan. Sanat jaetaan vaikkapa 100 sanan setteihin, joita käyttäjän oletetaan harjoittelevan, kunnes hän saa tarpeeksi monta oikein vastattua putkeen. Yhden setin harjoituksissa voisi myös olla kaksi eri vaikeustasoa, joista helpoimmassa aloitetaan setin harjoittelu 'tyhjästä', eli vastauksen kirjoittamisen sijaan tulee valita oikea vaihtoehto monivalintana. Kun käyttäjä läpäisee helpon vaikeustason, voi edetä vaikeammalle tasolle, jossa tulee vastata kirjoittamalla sana vastauskenttään.

## Asennusohjeet

Lataa sovellus githubista. Seuraavat komennot ajetaan kaikki projektin rootista. Ensin luo uusi virtual environment komennolla:
``` bash
python3 -m venv venv
```
Voit hakea tarvittavat python paketit komennolla:
``` bash
pip install -r requirements.txt
```
Muista luoda Postgress tietokanta ja luoda taulut schemasta:
``` bash
psql -f schema.sql
```
Ohjelma tarvitsee myös `.env` tiedoston projektin roottiin, jossa on seuraavat tiedot:
```
SECRET_KEY= *Luo salainen avain esim. pythonin secrets-moduulilla: secrets.token_hex(16) ja liitä se tähän kohtaan*
DATABASE_URL=postgresql+psycopg2://
ADMIN_USERNAME=admin
ADMIN_PASSWORD=salasana
```
Ohjelma käynnistyessään yrittää luoda admin-tilin annetulla nimellä ja salasanalla.

Aja ohjelma paikallisesti flaskin avulla:
``` bash
flask run
```

Sovelluksen tulisi olla nyt käytettävissä osoitteessa: http://127.0.0.1:5000/

## Heroku

Luo Heroku versio sovelluksesta käyttämällä kurssin ohjeita apuna. Ohjelmaa voi testata osoitteessa [Ruotsitreeni](https://tsoha-ruotsitreeni.herokuapp.com/). Olen tehnyt admin-tilin, jos haluat kokeilla uusien harjoitusten tai sanojen tekoa (nimi 'admin' ja salasana *yllapito*).

## Sovelluksen toteutetut ominaisuudet

- Käyttäjätili salasanalla. Käyttäjätilisivulta näkee hieman tilastointia kaikista vastauksista. Käyttäjä voi nyt poistaa itsensä tai muuttaa salasanaa (admin-tili ei voi poistaa itseään).
- Admin-tilillä voi luoda uusia harjoituksia, eli antaa harjoitukselle nimi sekä kuvaus.
- Harjoituksen luonnin jälkeen siirrytään luomaan uusia sanoja.
- Sanat liittyvät jokainen yhteen harjoitukseen. Sanalla on suomenkielinen ja ruotsinkielinen kenttä, sekä kuva.
- Sanoille voidaan myös antaa monivalinnan vastauksia listassa. Jos vääriä vastausvaihtoehtoja ei anna, niin sovellus valitsee satunnaisesti muista sanoista.
- Harjoitukset voi kuitenkin muuttaa näkymättömiksi, jolloin tavalliset käyttäjät eivät niitä kykene näkemään.
- Harjoituksissa ei ole toteutettuna kuin ensimmäinen monivalintaan liittyvä vaikeusaste.
- Vieraskirja (HypeZone) näkyy pääsivulla oikealla harjoitusten vieressä. Admin-tili voi 'poistaa' viestejä eli tehdä ne näkymättömiksi muille käyttäjille. Viesteissä näkyy kirjoittaja ja viestin sisältö. Poisto tapahtuu klikkaamalla viestiä listassa. Admin voi myös siirtyä katsomaan kyseisen viestin kirjoittajan käyttäjätilisivua, jos klikkaa käyttäjän nimeä poistokyselyssä.
- Lomakkeilla on nyt javascript tarkastusta, jotta säästyy turhilta submiteilta.
- Admin voi myös etsiä nimellä käyttäjiä käyttäjätililtä.

## Puuttuvat ominaisuudet

- Sanoja tai harjoituksia ei voi vielä poistaa tai muuttaa.
- Harjoitusten nimeä tai selostusta ei voi muuttaa. Harjoitusta ei voi poistaa.
- Käyttäjä ei voi vielä harjoitella vastausta ilman monivalintaa.
- Harjoitussivulla voisi näyttää tilastointia liittyen vain kyseiseen harjoitukseen.

## Sovelluksen ominaisuudet (aikaisempi suunnitelma)

- Käyttäjällä on tili, johon liittyy salasana ja jonkinlainen tilastointi per harjoitukset (esim. onnistumisprosentti). 
- Käyttäjä voi myös poistaa itsensä sovelluksesta.
- Admin-tilillä voidaan luoda uusia harjoituksia käyttäjille.
- Admin voi lisätä sanoja ja niiden kuvia tietokantaan ja liittää niitä eri harjoituksiin.
- Admin voi määrittää sanoille monivalintojen vaihtoehdot itse tai antaa järjestelmän valita satunnaisia ruotsin kielisiä sanoja vääriksi vastauksiksi.
- Admin voi muokata valmiita sanoja ja poistaa niitä harjoituksista tai koko sovelluksesta.
- Admin-tili pystyy näkemään käyttäjien tiedot ja mahdollisesti poistamaan käyttäjiä.
- Käyttäjät voivat aloittaa harjoituksien teon ja tehdä niitä, kunnes läpäisee harjoituksen molemmat vaikeustasot.
- Sovellus muistaa läpipäästyt harjoitukset.
- Käyttäjät pystyvät kirjoittamaan kaikille avoimeen vieraskirjaan toisilleen opiskeluun innostavia viestejä.
- Liian innostavat viestit voidaan adminin toimesta poistaa.
