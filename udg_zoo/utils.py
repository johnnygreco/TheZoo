def hsc_map_url(ra, dec):
    url = 'https://hscdata.mtk.nao.ac.jp/hsc_ssp/dr1/s16a/hscMap/'
    url += '#%7B%22tract%22%3A%22s16a_wide%2F9560%22%2C%22view%22%'
    url += '3A%7B%22center%22%3A%7B%22lat%22%3A'+str(ra)+'%2C%22lng%22%3A'
    url += str(dec)+'%7D%2C%22zoom%22%3A18%7D%2C%22colorFilter%22%3A%22SDSS%'
    url += '20True%20Color%22%2C%22colorFilter%2Fparams%2FSDSS%20True%20Color'
    url += '-1%22%3A%7B%22bias%22%3A0%2C%22log_a%22%3A10.819778284410283%2C%22format'
    url += '%22%3A%22png%22%2C%22filters%22%3A%5B%22I%22%2C%22R%22%2C%22G%22%5D%7D%7D'
    return url
