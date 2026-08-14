# Introdução
## Contexto
A empresa Jovi, internacionalmente chamada de vivo, utiliza-se de várias APIs internas para auxiliar na gestão de seus negócios. Nesse sentido, uma dessas APIs é a do vivoCloud, que serve para armazenar dados locais na nuvem da JOVI(vivo).

Porém, essa api tem um limite de 50 requisições por segundo e conforme a quantidade de requisições por segundo aumenta, o tempo de resposta da api também aumenta. Em condições normais, esse aumento é relativamente pequeno. Entretanto, quando a
carga se aproxima da capacidade máxima de processamento da infraestrutura, o tempo de resposta
cresce rapidamente e pode comprometer a experiência do usuário, os acordos de nível de serviço e a
disponibilidade do sistema.

## Proposta

Diante disso, nós alunos de Engenharia de Software da FIAP propomos a criação de um modelo matemático e computacional para analisar o comportamento dessa API sob pressão e documentar facilmente os dados obtidos.

## Objetivos