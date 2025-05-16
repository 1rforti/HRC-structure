# Holdem Resources Structure Generator

**Em Desenvolvimento** 🚀

Este é um software desenvolvido em Python para auxiliar os usuários do software [Holdem Resources](https://www.holdemresources.net/) na criação de estruturas de payouts solicitadas pelo software como entrada. O código transforma o arquivo .xml fornecido pelo site [SharkScope](https://pt.sharkscope.com/), acessível aos assinantes Gold na aba "Encontrar um torneio", em um arquivo .json que o HRC é capaz de ler.

## Pré-requisitos

Antes de instalar o software, é necessário baixar e instalar o Tesseract. Certifique-se de seguir as instruções abaixo para uma instalação adequada.

### Instalação do Tesseract

1. Baixe e instale o Tesseract-OCR versão 5.3.3.20231005 (64 bits) no diretório C:\Program Files\Tesseract-OCR da sua máquina: [Download Tesseract](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe)

   **OU**

   Para versões mais antigas, acesse [https://digi.bib.uni-mannheim.de/tesseract/](https://digi.bib.uni-mannheim.de/tesseract/) para opções de 32 e 64 bits.

   Repositório do Tesseract: [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

## Por que usar este software?

Não todos os usuários possuem Python instalado e, também por conveniência, para que as atualizações cheguem automaticamente aos usuários, optei por criar um arquivo de instalação, bem como um arquivo `main.exe`. Isso permite uma experiência mais conveniente ao executar o código/software.

## Aviso sobre Antivírus

**Atenção:** Devido à natureza dos arquivos executáveis, alguns antivírus podem sinalizar o software como um falso positivo de malware. No entanto, você pode confiar na integridade do software. Estou constantemente em contato com o suporte da Microsoft para resolver esse empecilho, mas o processo é demorado, especialmente quando estou frequentemente alterando os códigos.

Eu, Ricardo de Souza Forti, estou à disposição para quaisquer esclarecimentos a respeito da integridade do software, através do meu e-mail [ricardoforti@hotmail.com](mailto:ricardoforti@hotmail.com). É possível me encontrar não só por ele, mas facilmente por uma pesquisa rápida nas redes sociais. Sou Jogador profissional de Poker, atuo pelo maior time de poker do mundo, a 4betpokerteam há 3 anos, o que amplia quaisquer referências positivas.

Os executaveis, também foram todos assinados por mim artavés do OpenSSL, voce também pode seguir as etapas abaixo para verificar a integridade do aplicativo

## Verificação de Assinatura

Para garantir a integridade e autenticidade do software, siga as instruções abaixo para verificar a assinatura digital usando o certificado público fornecido.

### Passo 1: Baixar o Certificado Público

Certifique-se de ter o certificado público `certificado_publico.cer` baixado no seu sistema. Você pode encontrar o certificado na [pasta do repositório](https://github.com/1rforti/HRC-structure/blob/master/certificado_publico.cer).

### Passo 2: Verificar a Assinatura

Abra um terminal ou prompt de comando e navegue até a pasta onde o software está instalado. Execute o seguinte comando para verificar a assinatura digital:

```bash
openssl smime -verify -inform der -noverify -in main.exe -content main.exe -certfile certificado_publico.cer

```
Se a verificação for bem-sucedida, você verá uma mensagem indicando que a assinatura é válida.

Em caso de dúvidas ou problemas, entre em contato pelo e-mail ricardoforti@hotmail.com.



### Novas Funcionalidades 🚀🚀🚀

Converta as imagens das estruturas baixadas do pokercraft do GGPoker em JSON para o HRC. [Veja como](https://www.youtube.com/watch?v=menrJLgvrGU).

## Instruções de Instalação em Vídeo

[Assista às instruções de instalação passo a passo no YouTube](https://youtu.be/rWaHJYKbLtQ)

## Como Instalar:

1. **Baixe o Repositório:**
   - Clique em "Code" na parte superior deste repositório e selecione "Download ZIP" para baixar o repositório como um arquivo ZIP. Ou baixe diretamente [aqui](https://github.com/1rforti/HRC-structure/archive/refs/heads/master.zip).

2. **Descompacte o Arquivo:**
   - Descompacte o arquivo ZIP baixado. Você agora terá uma pasta chamada "HRC-structure-master".

3. **Crie um Diretório:**
   - Abra o Explorador de Arquivos.
   - Navegue até o disco "C:\".
   - Crie um diretório com o nome exato "C:\HRCStructureHHHHeadsUp". Certifique-se de usar esse nome específico para garantir o funcionamento correto do software.

4. **Mova os Arquivos:**
   - Abra a pasta "HRC-structure-master".
   - Selecione todos os arquivos e pastas.
   - Mova-os para o diretório "C:\HRCStructureHHHHeadsUp" que você acabou de criar.

5. **Criar Atalho na Barra de Ferramentas:**
   - Encontre o arquivo `main.exe` dentro do diretório "C:\HRCStructureHHHHeadsUp".
   - Clique com o botão direito no arquivo `main.exe` e escolha "Enviar para" > "Desktop (criar atalho)".
   - Mova o atalho criado para a barra de ferramentas para facilitar o acesso.

6. **Configurar Atalho para Executar como Administrador:**
   - Localize o atalho `main.exe` que você moveu para o Desktop ou a Barra de Ferramentas.
   - Clique com o botão direito no atalho `main.exe` e escolha "Propriedades".
   - Na guia "Atalho", clique em "Avançado...".
   - Marque a opção "Executar como administrador" e clique em "OK".
   - Confirme as alterações clicando em "OK" novamente nas propriedades.

7. Agora, ao clicar no atalho na barra de ferramentas, o software será executado com as permissões de administrador.

## Como Usar:

1. Siga as instruções para configurar a estrutura de payouts desejada.
2. O software gerará o arquivo .json pronto para ser usado no Holdem Resources.

## Suporte

Para qualquer dúvida ou problema, sinta-se à vontade para entrar em contato pelo e-mail [ricardoforti@hotmail.com](mailto:ricardoforti@hotmail.com).
