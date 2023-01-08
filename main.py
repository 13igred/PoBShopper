"""
Written by:
13igred
Version 0.1 - 08-01-23

The goal of the application is to provide users of PoB a quicker and easier way to price a build they found online.
It requires the user provide a poesessid - this key should be kept secret by the user.
Currently there is little security to protect the users poesessid if they choose to save it to file.

Future works
- Add the ability to search for rare items
- Try and get GGG to provide the ability to use oauth
- improve the readability of the auto price feature

Attributed Icon Authors:
Dollar icons created by Gregor Cresnar - Flaticon
Home button icons created by Freepik - Flaticon
Diamond icons created by prettycons - Flaticon
Star icons created by Pixel perfect - Flaticon
Shield icons created by Payungkead - Flaticon
"""



import customtkinter as ctk
from PIL import Image
from threading import *
import classes.PoBClass as PoBClass
import PricingRequests
import time
import webbrowser
import ItemMods


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode('Dark')
        self.title("PoB Shopper")
        self.geometry("900x600")
        self.pob = None
        self.loaded = False

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # # load images with light and dark mode image
        imagePath = "./resources/images/"
        self.logoImage = ctk.CTkImage(Image.open(imagePath + "Pobicon.png"), size=(26, 26))
        self.homeImage = ctk.CTkImage(Image.open(imagePath + "home.png"), size=(26, 26))
        self.gemImage = ctk.CTkImage(Image.open(imagePath + "diamond.png"), size=(26, 26))
        self.uniqueImage = ctk.CTkImage(Image.open(imagePath + "star.png"), size=(26, 26))
        self.raresImage = ctk.CTkImage(Image.open(imagePath + "shield.png"), size=(26, 26))
        self.autobuyImage = ctk.CTkImage(Image.open(imagePath + "dollar-symbol.png"), size=(26, 26))

        # todo: enable league selection
        # define trade url
        self.league = 'Sanctum'

        self.tradeUrlRoot = 'https://www.pathofexile.com/trade/search/' + self.league + '/'

        self.processId = ''

        with open('./UserDetails.txt', 'r') as file:
            data = file.read()
        file.close()
        if data != '':
            self.processId = data

        # define fonts
        self.fontTitle = ctk.CTkFont(family='Roboto', size=20, weight='bold')
        self.fontSideMenu = ctk.CTkFont(family='Roboto', size=18)
        self.fontText = ctk.CTkFont(family='Roboto', size=18)
        self.fontTableHeader = ctk.CTkFont(family='Roboto', size=16, weight='bold')
        self.fontTableText = ctk.CTkFont(family='Roboto', size=16)
        self.fontSmallText = ctk.CTkFont(family='Roboto', size=12)

        # create navigation frame
        self.navigationFrame = ctk.CTkFrame(self, corner_radius=0)
        self.navigationFrame.grid(row=0, column=0, sticky="nsew")
        self.navigationFrame.grid_rowconfigure(9, weight=1)

        self.navigationFrameTitle = ctk.CTkLabel(self.navigationFrame, text=" PoB Shopper",
                                                                image=self.logoImage,
                                                                compound="left",
                                                                font=self.fontTitle)
        self.navigationFrameTitle.grid(row=0, column=0, padx=20, pady=20)

        self.homeButton = ctk.CTkButton(self.navigationFrame, corner_radius=0, height=40, border_spacing=10,
                                                    text="                     Home",
                                                    fg_color="transparent", text_color=("gray10", "gray90"),
                                                    hover_color=("gray70", "gray30"),
                                                    image=self.homeImage, anchor="w",
                                                    command=self.homeButtonEvent,
                                                    font=self.fontSideMenu)
        self.homeButton.grid(row=1, column=0, sticky="ew")

        self.gemFrameButton = ctk.CTkButton(self.navigationFrame, corner_radius=0, height=40,
                                                    border_spacing=10, text="                      Gems",
                                                    fg_color="transparent", text_color=("gray10", "gray90"),
                                                    hover_color=("gray70", "gray30"),
                                                    image=self.gemImage, anchor="w",
                                                    command=self.gemButtonEvent,
                                                    font=self.fontSideMenu)
        self.gemFrameButton.grid(row=2, column=0, sticky="ew")

        self.uniqueFrameButton = ctk.CTkButton(self.navigationFrame, corner_radius=0, height=40,
                                                    border_spacing=10, text="        Unique Items",
                                                    fg_color="transparent", text_color=("gray10", "gray90"),
                                                    hover_color=("gray70", "gray30"),
                                                    image=self.uniqueImage, anchor="w",
                                                    command=self.uniqueButtonEvent,
                                                    font=self.fontSideMenu)
        self.uniqueFrameButton.grid(row=3, column=0, sticky="ew")

        self.itemFrameButton = ctk.CTkButton(self.navigationFrame, corner_radius=0, height=40,
                                               border_spacing=10, text="                       Rares",
                                               fg_color="transparent", text_color=("gray10", "gray90"),
                                               hover_color=("gray70", "gray30"),
                                               image=self.raresImage, anchor="w",
                                               command=self.itemButtonEvent,
                                               font=self.fontSideMenu)
        self.itemFrameButton.grid(row=4, column=0, sticky="ew")

        self.autoPriceFrameButton = ctk.CTkButton(self.navigationFrame, corner_radius=0, height=40,
                                               border_spacing=10, text="             Auto Pricer",
                                               fg_color="transparent", text_color=("gray10", "gray90"),
                                               hover_color=("gray70", "gray30"),
                                               image=self.autobuyImage, anchor="w",
                                               command=self.autoPriceButtonEvent,
                                               font=self.fontSideMenu)
        self.autoPriceFrameButton.grid(row=5, column=0, sticky="ew")

        self.versionLabel = ctk.CTkLabel(master=self.navigationFrame, text='PoB Shopper                   Version: 0.1',
                                         font=self.fontSmallText, text_color=('gray50'))
        self.versionLabel.place(x=2, y=577)

        # create home frame
        self.homeFrame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.homeFrame.grid_columnconfigure(0, weight=1)

        self.spacingLbl = ctk.CTkLabel(master=self.homeFrame, text='')
        self.spacingLbl.pack(pady=50)

        self.ePOESESSID = ctk.CTkEntry(master=self.homeFrame, width=200, placeholder_text='POESESSID',
                                       font=self.fontText, show='*')
        self.ePOESESSID.pack(pady=12, padx=10)

        # test if processId was saved if it is populate the field
        if self.processId != '':
            self.ePOESESSID.insert(0, self.processId)

        self.helpBtn = ctk.CTkButton(master=self.homeFrame, text='?', width=30, font=self.fontText,
                                     command=self.openHelp)
        self.helpBtn.place(x=460, y=140)

        self.ePobCode = ctk.CTkEntry(master=self.homeFrame, width=200, placeholder_text='POB URL/Code',
                                     font=self.fontText)
        self.ePobCode.pack(pady=12, padx=10)

        self.comboboxLeague = ctk.CTkComboBox(master=self.homeFrame,
                                              values=['League SC', 'League HC', 'Standard', 'Hardcore'],
                                              command=self.selectLeague)
        self.comboboxLeague.pack(pady=12, padx=10)

        self.confButton = ctk.CTkButton(master=self.homeFrame, width=160, text='Confirm', command=self.updatePob,
                                        font=self.fontText)
        self.confButton.pack(pady=12, padx=10)

        self.rememberSessId = ctk.CTkCheckBox(master=self.homeFrame, text='Remember me',
                                        onvalue=True, offvalue=False)
        self.rememberSessId.pack(pady=12, padx=10)

        # create gem frame
        self.gemMaster = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.gemFrame = ctk.CTkFrame(master=self.gemMaster)

        # create uniques frame
        self.uniqueMaster = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.uniqueFrame = ctk.CTkFrame(master=self.uniqueMaster)

        # create item frame
        self.itemMaster = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.itemFrame = ctk.CTkFrame(master=self.itemMaster)

        # create auto price frame
        self.autoPriceMaster = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.autoPriceTextbox = ctk.CTkTextbox(self, width=500, height=350)

        # select default frame
        self.selFrameByName("home")

    def openHelp(self):
        # opens up help page on how to find process id
        webbrowser.open_new_tab('http://www.vhpg.com/how-to-find-poe-session-id/')

    def selectLeague(self, selection):
        if selection == 'League SC':
            self.league = 'Sanctum'
        if selection == 'League HC':
            self.league = 'Hardcore%20Sanctum'
        if selection == 'Standard':
            self.league = 'Standard'
        if selection == 'Hardcore':
            self.league = 'Hardcore'

        self.tradeUrlRoot = 'https://www.pathofexile.com/trade/search/' + self.league + '/'

    def updatePob(self):
        # populates pob data
        if self.rememberSessId.get():
            with open('./UserDetails.txt', 'r+') as file:
                # absolute file positioning
                file.seek(0)
                # to erase all data
                file.truncate()
                # write data
                file.write(self.ePOESESSID.get())
        file.close()

        # todo: error handling
        self.pob = PoBClass.POB(self.ePobCode.get())

    def threading(self):
        # create thread when auto pricing so as to not lock out the UI
        t1 = Thread(target=self.startShopping)
        t1.start()

    def startShopping(self):
        # auto shopping process
        self.loaded = False
        tradeUrl = 'https://www.pathofexile.com/trade/search/' + self.league + '/'
        self.updateAutoPriceTextbox('Now loading data, please wait...\n\n\n')
        # lblLoad = ctk.CTkLabel(master=self.autoPriceMaster, text='Loading please wait...')
        # lblLoad.pack(pady=5, padx=10)

        # populate gem pricing and trade url data
        for idx in range(len(self.pob.gems)):
            gemIdx = 0
            for gem in self.pob.gems[idx]['gems']:
                # check that the gem is a skill gem and not from an item
                if gem['type'] != 'none':
                    # request data using query builder
                    response, delay, statusCode = PricingRequests.RequestGemJson(gem, self.ePOESESSID.get(), self.league)
                    time.sleep(delay)

                    if statusCode == 200:
                        # request the average price of the first 10 hits
                        price = PricingRequests.RequestPriceData(response, self.ePOESESSID.get())
                        self.pob.gems[idx]['gems'][gemIdx]['price'] = price
                        self.pob.gems[idx]['gems'][gemIdx]['tradeUrl'] = tradeUrl + response['id']
                        displayGemInfo(gem)
                        time.sleep(delay)

                updateString = '----------------------------\nName: ' + gem['name'] + '\nAverage Price: ' \
                               + str(gem['price']) + '\nTrade Url: ' + gem['tradeUrl'] \
                               + '\n----------------------------\n'
                # update the textbox
                self.updateAutoPriceTextbox(updateString)
                gemIdx += 1

        uniqueIdx = 0
        for item in self.pob.uniques:
            modValue, modId = ItemMods.UniqueMods(item['explicits'])
            response, delay, statusCode = PricingRequests.requestUniqueJson(item, modId, modValue, self.ePOESESSID.get(), self.league)
            time.sleep(delay)

            if statusCode == 200:
                price = PricingRequests.RequestPriceData(response, self.ePOESESSID.get(), self.league)
                self.pob.uniques[uniqueIdx]['price'] = price
                self.pob.uniques[uniqueIdx]['tradeUrl'] = tradeUrl + response['id']
                displayItemInfo(item)
                time.sleep(delay)

            uniqueIdx += 1
            updateString = '----------------------------\nName: ' + item['name'] + '\nAverage Price: ' + str(item['price']) + '\nTrade Url: ' + item['tradeUrl'] + '\n----------------------------\n'
            self.updateAutoPriceTextbox(updateString)
        self.loaded = True

    def updateAutoPriceTextbox(self, info):
        self.autoPriceTextbox.insert("end", info)

    def comboboxGemCallback(self, choice):
        selGem = None

        for idx in range(len(self.pob.gems)):
            for gem in self.pob.gems[idx]['gems']:
                if choice in gem['name']:
                    selGem = gem
                    break

        for widget in self.gemFrame.winfo_children():
            widget.destroy()

        if selGem:
            # fix gem type
            # phantasmal
            if selGem['type'] == 'Alternate3':
                typeName = 'Phantasmal'
            # divergent
            if selGem['type'] == 'Alternate2':
                typeName = 'Divergent'
            # anomalous
            if selGem['type'] == 'Alternate1':
                typeName = 'Anomalous'
            if selGem['type'] == 'Default':
                typeName = 'Default'

            lblName = ctk.CTkLabel(master=self.gemFrame, text='Name: ', font=self.fontTableHeader)
            lblName.place(x=10, y=10)
            lblGName = ctk.CTkLabel(master=self.gemFrame, text=selGem['name'], font=self.fontTableText)
            lblGName.place(x=100, y=10)

            lblLvl = ctk.CTkLabel(master=self.gemFrame, text='Level: ', font=self.fontTableHeader)
            lblLvl.place(x=10, y=60)
            lblGLvl = ctk.CTkLabel(master=self.gemFrame, text=selGem['level'], font=self.fontTableText)
            lblGLvl.place(x=100, y=60)

            lblQual = ctk.CTkLabel(master=self.gemFrame, text='Quality: ', font=self.fontTableHeader)
            lblQual.place(x=10, y=110)
            lblGQual = ctk.CTkLabel(master=self.gemFrame, text=selGem['quality'], font=self.fontTableText)
            lblGQual.place(x=100, y=110)

            lblType = ctk.CTkLabel(master=self.gemFrame, text='Type: ', font=self.fontTableHeader)
            lblType.place(x=10, y=160)
            lblGType = ctk.CTkLabel(master=self.gemFrame, text=typeName, font=self.fontTableText)
            lblGType.place(x=100, y=160)

            if selGem['price'] != 0:
                lblPrice = ctk.CTkLabel(master=self.gemFrame, text='Price: ', font=self.fontTableHeader)
                lblPrice.place(x=10, y=210)
                lblGPrice = ctk.CTkLabel(master=self.gemFrame, text=str(selGem['price']) + ' Chaos',
                                         font=self.fontTableText)
                lblGPrice.place(x=100, y=210)

            btn = ctk.CTkButton(master=self.gemFrame, text='Open Trade', width=160,
                                command=lambda: self.openGemTrade(selGem), font=self.fontTableText)
            btn.place(x=10, y=310)

    def comboboxUniqueCallback(self, choice):
        selUnique = None

        for idx in range(len(self.pob.gems)):
            for unique in self.pob.uniques:
                if choice in unique['name']:
                    selUnique = unique
                    break

        for widget in self.uniqueFrame.winfo_children():
            widget.destroy()

        lblName = ctk.CTkLabel(master=self.uniqueFrame, text='Name:', font=self.fontTableHeader)
        lblName.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        lblGName = ctk.CTkLabel(master=self.uniqueFrame, text=selUnique['name'], font=self.fontTableText)
        lblGName.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        row = 1
        for implicit in selUnique['implicits']:
            if len(implicit) > 40:
                name = implicit[0:40] + '...'
            else:
                name = implicit

            lblImplc = ctk.CTkLabel(master=self.uniqueFrame, text='Implicit:', font=self.fontTableHeader)
            lblImplc.grid(row=row, column=0, padx=10, pady=10, sticky='w')
            lblImplc = ctk.CTkLabel(master=self.uniqueFrame, text=name, font=self.fontTableText)
            lblImplc.grid(row=row, column=1, padx=10, pady=10, sticky='w')
            checkboxImplc = ctk.CTkCheckBox(master=self.uniqueFrame, text='',
                                            command=lambda i=implicit: self.checkboxUniqueEvent(i, checkboxImplc.get()),
                                            onvalue=True, offvalue=False)
            checkboxImplc.grid(row=row, column=2, padx=10, pady=10, sticky='e')
            row += 1

        for explicit in selUnique['explicits']:
            if len(explicit) > 50:
                name = explicit[0:50] + '...'
            else:
                name = explicit

            lblExpli = ctk.CTkLabel(master=self.uniqueFrame, text='Explicit:', font=self.fontTableHeader)
            lblExpli.grid(row=row, column=0, padx=10, pady=10, sticky='w')
            lblExpli = ctk.CTkLabel(master=self.uniqueFrame, text=name, font=self.fontTableText)
            lblExpli.grid(row=row, column=1, padx=10, pady=10, sticky='w')
            checkboxExpli = ctk.CTkCheckBox(master=self.uniqueFrame, text='',
                                            command=lambda i=explicit: self.checkboxUniqueEvent(i, checkboxExpli.get()),
                                            onvalue=True, offvalue=False)
            checkboxExpli.grid(row=row, column=2, padx=10, pady=10, sticky='e')
            row += 1

        if selUnique['price'] != 0:
            lblPrice = ctk.CTkLabel(master=self.uniqueFrame, text='Price: ', font=self.fontTableHeader)
            lblPrice.grid(row=row, column=0, padx=10, pady=10, sticky='w')
            lblGPrice = ctk.CTkLabel(master=self.uniqueFrame, text=str(selUnique['price']) + ' Chaos',
                                     font=self.fontTableText)
            lblGPrice.grid(row=row, column=1, padx=10, pady=10, sticky='w')
            row += 1

        lblHiddenSpacing = ctk.CTkLabel(master=self.uniqueFrame, text='')
        lblHiddenSpacing.grid(row=row, column=0, padx=50)

        btn = ctk.CTkButton(master=self.uniqueFrame, text='Open Trade', width=160,
                            command=lambda: self.openUniqueTrade(selUnique), font=self.fontTableText)
        btn.grid(row=row+1, column=1)

    # todo: enable filtering by item mods
    def checkboxUniqueEvent(self, choose, checkbox):
        print(choose)
        print(checkbox)

    def selFrameByName(self, name):
        # set button color for selected button
        self.homeButton.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.gemFrameButton.configure(fg_color=("gray75", "gray25") if name == "gems" else "transparent")
        self.uniqueFrameButton.configure(fg_color=("gray75", "gray25") if name == "uniques" else "transparent")
        self.itemFrameButton.configure(fg_color=("gray75", "gray25") if name == "items" else "transparent")
        self.autoPriceFrameButton.configure(fg_color=("gray75", "gray25") if name == "autoprice" else "transparent")

        # show selected frame
        if name == "home":
            self.homeFrame.grid(row=0, column=1, sticky="nsew")
        else:
            self.homeFrame.grid_forget()

        if name == "gems" and self.pob is not None:
            self.gemMaster.grid(row=0, column=1, sticky="nsew")
            self.populateGemFrame()
            self.gemFrame.pack(pady=20, padx=60, fill='both', expand=True)
        else:
            self.gemMaster.grid_forget()

        if name == "uniques" and self.pob is not None:
            self.uniqueMaster.grid(row=0, column=1, sticky="nsew")
            self.populateUniqueFrame()
            self.uniqueFrame.pack(pady=20, padx=60, fill='both', expand=True)
        else:
            self.uniqueMaster.grid_forget()

        if name == "items" and self.pob is not None:
            self.itemMaster.grid(row=0, column=1, sticky="nsew")
            self.itemFrame.pack(pady=20, padx=60, fill='both', expand=True)
        else:
            self.itemMaster.grid_forget()

        if name == "autoprice" and self.pob is not None:
            self.autoPriceMaster.grid(row=0, column=1, sticky="nsew")
            self.populateAutoPrice()
        else:
            self.autoPriceMaster.grid_forget()
            self.autoPriceTextbox.grid_forget()

        if self.pob is None:
            self.homeFrame.grid(row=0, column=1, sticky="nsew")
            name = 'home'
            self.homeButton.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
            self.gemFrameButton.configure(fg_color=("gray75", "gray25") if name == "gems" else "transparent")
            self.uniqueFrameButton.configure(fg_color=("gray75", "gray25") if name == "uniques" else "transparent")
            self.itemFrameButton.configure(fg_color=("gray75", "gray25") if name == "items" else "transparent")
            self.autoPriceFrameButton.configure(fg_color=("gray75", "gray25") if name == "autoprice" else "transparent")

    def homeButtonEvent(self):
        self.selFrameByName("home")

    def gemButtonEvent(self):
        self.selFrameByName("gems")

    def uniqueButtonEvent(self):
        self.selFrameByName("uniques")

    def itemButtonEvent(self):
        self.selFrameByName("items")

    def autoPriceButtonEvent(self):
        self.selFrameByName("autoprice")

    def populateGemFrame(self):

        for widget in self.gemMaster.winfo_children():
            widget.destroy()

        gemOptions = []
        for idx in range(len(self.pob.gems)):
            for gem in self.pob.gems[idx]['gems']:
                gemOptions.append(gem['name'])

        lblInfoTitle = ctk.CTkLabel(master=self.gemMaster, text='Select Gem',
                                         font=self.fontTitle)
        lblInfoTitle.pack(padx=20, pady=10)
        self.comboboxGem = ctk.CTkOptionMenu(master=self.gemMaster, values=gemOptions,
                                             command=self.comboboxGemCallback,
                                             width=400)
        self.comboboxGem.pack(padx=20, pady=10)
        self.gemFrame = ctk.CTkFrame(master=self.gemMaster)
        self.comboboxGemCallback(gemOptions[0])
        
    def populateUniqueFrame(self):
        for widget in self.uniqueMaster.winfo_children():
            widget.destroy()
        
        uniqueOptions = []
        
        for unique in self.pob.uniques:
            uniqueOptions.append(unique['name'])

        lblInfoTitle = ctk.CTkLabel(master=self.uniqueMaster, text='Select Unique',
                                    font=self.fontTitle)
        lblInfoTitle.pack(padx=20, pady=10)

        self.comboboxUnqiue = ctk.CTkOptionMenu(master=self.uniqueMaster, values=uniqueOptions,
                                                command=self.comboboxUniqueCallback,
                                                width=400)
        self.comboboxUnqiue.pack(padx=20, pady=10)
        self.uniqueFrame = ctk.CTkFrame(master=self.uniqueMaster)
        self.comboboxUniqueCallback(uniqueOptions[0])

    def populateAutoPrice(self):
        for widget in self.autoPriceMaster.winfo_children():
            widget.destroy()

        lblInfoTitle = ctk.CTkLabel(master=self.autoPriceMaster, text='Auto Price Build',
                                    font=self.fontTitle)
        lblInfoTitle.pack(padx=10, pady=5)

        btn = ctk.CTkButton(master=self.autoPriceMaster, text='Start Auto Pricing', font=self.fontTableText,
                            command=self.threading)
        btn.pack(padx=20, pady=5)

        lblInfoTitle = ctk.CTkLabel(master=self.autoPriceMaster, text='Warning. This process takes ~3-5 minutes',
                                    font=self.fontSmallText)
        lblInfoTitle.pack(padx=20, pady=5)

        self.autoPriceTextbox.grid(row=0, column=1)

    def openGemTrade(self, selGem):
        response, delay, statusCode = PricingRequests.RequestGemJson(selGem, self.ePOESESSID.get(), self.league)
        url = self.tradeUrlRoot + response['id']
        webbrowser.open_new_tab(url)

    def openUniqueTrade(self, selUnique):
        modValue, modId = ItemMods.UniqueMods(selUnique['explicits'])
        response, delay, statusCode = PricingRequests.requestUniqueJson(selUnique, modId, modValue,
                                                                        self.ePOESESSID.get(), self.league)
        url = self.tradeUrlRoot + response['id']
        webbrowser.open_new_tab(url)

    def displayAutoPriceData(self):
        pass


def displayGemInfo(gem):
    print('---------------------')
    print('Name: ' + gem['name'])
    print('Level: ' + gem['level'])
    print('Quality: ' + gem['quality'])
    print('Quality Type: ' + gem['type'])
    print('Average Price: ' + str(gem['price']))
    print('Trade URL: ' + gem['tradeUrl'])
    print('---------------------')
    print()


def displayItemInfo(itemInfo):
    print('---------------------')
    print('Name: ' + itemInfo['name'])
    for text in itemInfo['implicits']:
        print('Implicits: ' + text)
    for text in itemInfo['explicits']:
        print('Explicits: ' + text)
    print('Average Price: ' + str(itemInfo['price']))
    print('Trade URL: ' + itemInfo['tradeUrl'])
    print('---------------------')
    print()


if __name__ == "__main__":
    app = App()
    app.resizable(width=False, height=False)
    app.mainloop()



