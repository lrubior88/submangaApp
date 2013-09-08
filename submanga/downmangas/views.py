############################################
# Luis E. Rubio Rodriguez --- 07/01/2013
# l.rubiorod@gmail.com
############################################

# Create your views here.

import httplib # Necesaria para hacer peticiones HTTP
import os

from django.http import HttpResponse,HttpResponseNotFound

def say_main(request):

    return HttpResponse('<h1>PAGINA PRINCIPAL</h1><br>'+
            '<br><h2> Submanga </h2><br>' + 

			'Bajar serie entera: /submanga/todos/nombreDeLaSerieEnSubmanga<br>'+
			'Bajar un rango de caps: /submanga/rango/nombreDeLaSerieEnSubmanga/ncapInicio/ncapFin<br>'+
			'Bajar un cap: /submanga/manga/nombreDeLaSerieEnSubmanga/ncap<br>'+

            '<br>(Eligiendo un Fansub):<br>'+
			'Bajar serie entera: /submanga/scan/todos/nombreDelFansub/nombreDeLaSerieEnSubmanga<br>'+
			'Bajar un rango de caps: /submanga/scan/rango/nombreDelFansub/nombreDeLaSerieEnSubmanga/ncapInicio/ncapFin<br>'+
			'Bajar un cap: /submanga/scan/manga/nombreDelFansub/nombreDeLaSerieEnSubmanga/ncap<br>' + 
           
            '<br><h2> MangaFox </h2><br>' + 

			'Bajar un rango de caps: /mangafox/rango/nombreDeLaSerieEnSubmanga/ncapInicio/ncapFin<br>'+
			'Bajar un cap: /mangafox/manga/nombreDeLaSerieEnSubmanga/ncap<br><br>' 
    )


def peticionHTTP(dominio, peticion):

    conn = httplib.HTTPConnection(dominio)
    conn.putrequest("GET", peticion)
    conn.putheader("User-Agent","Mozilla/5.0 (X11; U; Linux i686; es-ES; rv:1.9.2.11) Gecko/20101013 Ubuntu/10.04 (lucid) Firefox/3.6.11")
    conn.endheaders()
    conn.send("")
    r = conn.getresponse()
    print r.status, r.reason
    data = r.read()
    conn.close()

    return data

def downImage(dominio, rutaImg, directorio, nombre):

    try:
        data = peticionHTTP(dominio, rutaImg)
        if not os.path.isdir(directorio):
            os.mkdir(directorio)
        fichero = file( directorio + '/' + nombre, "wb" )
        fichero.write(data)
        fichero.close()
        print "Bajado:  " + nombre
    except:
        print "No se ha podido descargar la imagen"

def downManga(serv, serie, cap, num):

    if (int(serv) == 1):
        data = peticionHTTP('submanga.com', '/c/'+ str(num))
        info = data.split('<option value="')[-1]
        npag = info.split('">')[0]
    
    elif (int(serv) == 2):
        peticion = "/manga/"+str(serie)+"/v"+str(num)+"/c"+str(cap)+"/1.html"
        data = peticionHTTP('mangafox.me', peticion)
        info = data.split("pages=")[1]
        npag = info.split(";")[0]

    print 'NPAG:\n'+npag
    reitento=[]
    for i in range(1,int(npag)+1):
        reitento.append(i)

    while (len(reitento)>0):
        for i in reitento:
            print reitento
            try:
                if (int(serv) == 1):
                    peticion ="/c/"+str(num)+"/"+str(i)
                    data = peticionHTTP('submanga.com', peticion)

                    info = data.split('</table><div><a href=')[1]
                    info2 = info.split('img src="')[1]
                    url = info2.split('"/></a>')[0]
                    print 'URL: '+url

                    site = url.split('://')[1]
                    dominio = site.split('/')[0]
                    rutaImg = site.split('.com')[1]

                elif (int(serv) == 2):
                    peticion = "/manga/"+str(serie)+"/v"+str(num)+"/c"+str(cap)+"/"+str(i)+".html"
                    data = peticionHTTP('mangafox.me', peticion)

                    info = data.split('onclick="return enlarge()"><img src="')[1]
                    url = info.split('" onerror="')[0]
                    print 'URL:'+url
 
                    site = url.split('://')[1]
                    dominio = site.split('/')[0]
                    rutaImg = site.split('.net')[1]

                capitulo = cap
                if (int(capitulo)<10):
                    capitulo='0'+capitulo
                if (int(capitulo)<100):
                    capitulo='0'+capitulo

                pagina = str(i)
                if (int(pagina)<10):
                    pagina='0'+pagina

                downImage(dominio, rutaImg, serie, serie + capitulo + '_' + pagina + '.jpg')
                reitento.remove(i)
            except:
                print 'Pagina ' + str(i) + ' no cargada'


def bajarMangas(peticion, serie, begin, end):

    data = peticionHTTP('submanga.com', peticion)
    info = data.split('<strong>')[1]
    ncaps = info.split('</strong>')[0]
    fin = end
    if (int(ncaps) < int(end)):
        fin = ncaps

    if (int(fin) < int(begin)):
        print 'Capitulo no encontrado'
        return

    for i in range(int(begin),int(fin)+1):
        info = data.split('td class="s"><a href="http://submanga.com/'+str(serie)+'/'+str(i)+'/')[1]
        codigo = info.split('">')[0]
        print 'Codigo: '+codigo
        downManga(1, serie, str(i), codigo)

    print 'Fin de bucle'


def bajarMangasFox(peticion, serie, begin, end):

    data = peticionHTTP('mangafox.me', peticion)

    if (int(end) < int(begin)):
        print 'Capitulo no encontrado'
        return

    for i in range(int(begin),int(end)+1):
        busqueda ="/c"+str(i)
        info = data.split(busqueda)[0]
        vol = info.split("/v")[-1]
        print 'volumen: '+vol
        downManga(2, serie, str(i), vol)

    print 'Fin de bucle'

def bajarCodeManga(request, resource):
    
    serie = resource.split('/')[0]
    numero = resource.split('/')[1]
    code = resource.split('/')[2]

    print serie
    print numero   
    print code

    downManga(1, serie, numero, code)

    return HttpResponse("Ya ta")

def bajarCodeMangaFox(request, resource):
    
    serie = resource.split('/')[0]
    numero = resource.split('/')[1]
    code = resource.split('/')[2]

    print serie
    print numero   
    print code

    downManga(2, serie, numero, code)

    return HttpResponse("Ya ta")
    
def bajar1Manga(request, resource):

    serie = resource.split('/')[0]
    numero = resource.split('/')[1]
    print serie
    print numero

    peticion ='/'+serie+'/completa'
    print 'pido: '+peticion

    bajarMangas(peticion, serie, numero, numero)

    return HttpResponse("Ya ta")

def bajar1MangaFox(request, resource):

    serie = resource.split('/')[0]
    numero = resource.split('/')[1]
    print serie
    print numero

    peticion ='/manga/'+serie
    print 'pido: '+peticion

    bajarMangasFox(peticion, serie, numero, numero)

    return HttpResponse("Ya ta")

def bajarRangoMangas(request, resource):

    serie = resource.split('/')[0]
    begin = resource.split('/')[1]
    end = resource.split('/')[2]
    print serie
    print 'Empieza en '+begin+' y acaba en '+end

    peticion ='/' + serie + '/completa'
    print 'pido: '+ peticion

    bajarMangas(peticion, serie, begin, end)

    return HttpResponse("Ya ta")

def bajarRangoMangasFox(request, resource):

    serie = resource.split('/')[0]
    begin = resource.split('/')[1]
    end = resource.split('/')[2]
    print serie
    print 'Empieza en '+begin+' y acaba en '+end

    peticion ='/manga/'+serie
    print 'pido: '+peticion

    bajarMangasFox(peticion, serie, begin, end)
  
    return HttpResponse("Ya ta")

def bajarTodosMangas(request, resource):

    serie = resource
    print serie

    peticion ='/'+serie+'/completa'
    print 'pido: '+peticion

    bajarMangas(peticion, serie, 1, 5000)

    return HttpResponse("Ya ta")

def bajar1MangaScan(request, resource):

    fansub = resource.split('/')[0]
    serie = resource.split('/')[1]
    numero = resource.split('/')[2]
    print serie
    print numero
    print fansub

    peticion ='/'+serie+'/scanlation/'+fansub
    print 'pido: '+peticion

    bajarMangas(peticion, serie, numero, numero)

    return HttpResponse("Ya ta")

def bajarTodosMangasScan(request, resource):

    fansub = resource.split('/')[0]
    serie = resource.split('/')[1]
    print nombre
    print 'Fansub: '+ fansub +' Serie: '+ serie

    peticion ='/' + serie + '/scanlation/' + fansub
    print 'pido: '+peticion

    bajarMangas(peticion, serie, 1, 5000)

    return HttpResponse("Ya ta")


def bajarRangoMangasScan(request, resource):

    fansub = resource.split('/')[0]
    serie = resource.split('/')[1]
    begin = resource.split('/')[2]
    end = resource.split('/')[3]
    print serie
    print 'Fansub: '+fansub+'\nEmpieza en '+begin+' y acaba en '+end

    peticion ='/'+serie+'/scanlation/'+fansub
    print 'pido: '+peticion

    bajarMangas(peticion, serie, begin, end)

    return HttpResponse("Ya ta")

