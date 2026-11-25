import unittest
from datetime import date
from calculos import calcular,inss,irrf
class Teste(unittest.TestCase):
    def test_cenario(self):
        r=calcular(date(2025,9,8),date(2026,11,25),13000,'Trabalhado',20,15000,None,20000,'Saque-rescisão')
        self.assertEqual(r['avos'],3)
        self.assertEqual(r['proventos']['13º salário'],11916.67)
        self.assertEqual(r['retido'],20000)
        self.assertEqual(r['total'],round(r['liquido']+r['saque']+r['multa'],2))
    def test_aniversario(self):
        r=calcular(date(2025,9,8),date(2026,10,25),13000,'Indenizado',20,15000,None,20000,'Saque-aniversário')
        self.assertEqual(r['dias_aviso'],33)
        self.assertEqual(r['saque'],0)
        self.assertEqual(r['total'],round(r['liquido']+r['multa'],2))
    def test_impostos(self):
        self.assertEqual(inss(13000),988.09)
        self.assertEqual(irrf(5000,inss(5000)),0)
if __name__=='__main__': unittest.main()
