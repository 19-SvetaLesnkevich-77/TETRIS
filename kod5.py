from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QFrame,
    QMainWindow
    )
from PyQt5.QtCore import (
    Qt,
    QBasicTimer,
    QEvent,
    pyqtSignal
    )
from PyQt5.QtGui import (
    QColor,
    QPainter
    )
import typing
import random
import enum

'''
   определяем стандартные формы и цвета tetromino
   назовем семь фигур через IntEnum.Где "N"--это не фигура,и предстовл
   яет собой доску.Всегда создается только одина "N" 
'''

class T_ShapeNames(enum.IntEnum):
    N = 0 #
    O = 1 # квадрат
    I = 2 # строка из 4
    T = 3
    L = 4
    J = 5
    S = 6
    Z = 7

'''
Назначаем цвета для фигур
имена цветов задаются в виде строк ,выбранных из
списка доступных.Определяем цвета и вазвращаем функцией
QColor.colorNames()
'''

T_Colors = {
    T_ShapeNames.N : QColor(204,204,204,32),# нет цвета
    T_ShapeNames.O : QColor('yellow'),
    T_ShapeNames.I : QColor('cyan'),
    T_ShapeNames.T : QColor('purple'),
    T_ShapeNames.L : QColor('orange'),
    T_ShapeNames.J : QColor('blue'),
    T_ShapeNames.S : QColor('green'),
    T_ShapeNames.Z : QColor('red')
    }
'''
Присваиваем каждой фигуре свою форму и начальные координаты
каждая фигура описывается списком из четырех (x,y)кортежей,которые
определяют четыре ячейки с центром в координатной плоскости xy.
Чтобы повернуть фигуру влево,заменим кортеж:((-y,x) для (x,y) в оригинальном
T_Shapes.чтобы повернуть фигуру вправо,используем(y,-x)вместо (x,y)
'''

T_Shapes = {
    T_ShapeNames.N : ((0,0),(0,0),(0,0),(0,0)),
    T_ShapeNames.O : ((0,1),(1,1),(0,0),(1,0)),
    T_ShapeNames.I : ((-2,0),(-1,0),(0,0),(1,0)),
    T_ShapeNames.T : ((0,1),(-1,0),(0,0),(1,0)),
    T_ShapeNames.L : ((1,1),(-1,0),(0,0),(1,0)),
    T_ShapeNames.J : ((-1,1),(-1,0),(0,0),(1,0)),
    T_ShapeNames.S : ((-1,0),(0,0),(0,1),(1,1)),
    T_ShapeNames.Z : ((-1,1),(0,1),(0,0),(1,0))
    }

'''
создаем функцию make_bag(),так называемую "сумку" из семи имен
фигур в случайном порядке
'''

def make_bag() -> typing.List[T_ShapeNames] :
    bag = [ T_ShapeNames(v) for v in range(1,8) ]
    random.shuffle(bag)
    return bag

'''
определим класс наших игровых фигур,T_mo.Наша фигура имеет имя и цвет 
своей формы,а также свою форму из четырех(x,y)значений как определено в 
T_Shapes выше.  T_mo может вращаться,но обратим внимание,что методы
rotate_left() и rotate_right() не изменяют форму вызванного T_mo.Они 
вызывают новую фигуру,для замены старой.Это делается для того ,чтобы
протестировать вращение.Если новый повернутый T_mo является правильным,он
заменяет старый,но если это не так исходный T_mo остается неизменным. 
'''

class T_mo(object):
    def __init__(self, t_name: T_ShapeNames) :
        self.t_name = t_name
        self.t_color = T_Colors[t_name]
        self.coords = tuple( ((x,y) for (x,y) in T_Shapes[t_name]) )

    def color(self) -> QColor :
        return self.t_color

    '''
    вернем значения (х,у) одну из четырех ячеек T_mo
    '''
    def x(self, cell:int ) -> int :
        return self.coords[cell][0]
    def y(self, cell:int ) -> int :
        return self.coords[cell][1]

    '''
    Возврощаем миним и максим значения (х,у) игровых фигур
    '''
    def x_max(self) -> int :
        return max( (x for (x,y) in self.coords) )
    def x_min(self) -> int :
        return min( (x for (x,y) in self.coords) )
    def y_max(self) -> int :
        return max( (y for (x,y) in self.coords) )
    def y_min(self) -> int :
        return min( (y for (x,y) in self.coords) )

    '''
    возвращаем новую фигуру ,повернутую в лево или в право.
    '''
    def rotateLeft(self) :
        new_tmo = T_mo( self.t_name )
        new_tmo.coords = tuple( ((-y,x) for (x,y) in self.coords ) )
        return new_tmo
    def rotateRight(self) :
        new_tmo = T_mo( self.t_name )
        new_tmo.coords = tuple( ( (y,-x) for (x,y) in self.coords ) )
        return new_tmo

'''

'''

NO_T_mo = T_mo( T_ShapeNames.N )

'''
определяем игровое поле.класс Board устанавливает главное,рабочее окно и 
будет получать событыя нажатия клавиш.
'''
class Board(QFrame):

    '''
    определяем сигнал pyqtSignal строковым значением,этот сигнал срабатывает
    когда пишется количество очков в в строку состояния
    '''
    NewStatus = pyqtSignal(str)

    '''
    задаем размер доски 
    '''
    Columns = 10
    Rows = 22

    '''
    начальную скорость 
    '''
    StartingSpeed = 500

    def __init__(self, parent):
        super().__init__(parent)
        '''
        
        '''
        self.setFocusPolicy(Qt.StrongFocus)
        '''
        задаем темп игре
        '''
        self.timer = QBasicTimer()
        '''
        создаем переменную,где устоновленно True ,после чистки полных строк
        
        '''
        self.waitForNextTimer = False
        '''
        ставим но паузу нажатием клавиши p 
        '''
        self.isStarted = False
        self.isPaused = False
        '''
        создаем список ключей для клавиш
        '''
        self.validKeys = [ Qt.Key_Left, Qt.Key_Right, Qt.Key_D,
                           Qt.Key_Down, Qt.Key_Up, Qt.Key_Space,
                           Qt.Key_P ]
        '''
        создаем активную фигуру с индексом по центру
        '''
        self.curPiece = NO_T_mo
        self.curX = 0
        self.curY = 0
        '''
        активируем количество завершенных строк.
        '''
        self.completedLines = 0
        '''
        создаем "доску",где задокументированы все ячейки.активируем
        при вызове self.start()
        '''
        self.board = [] # тип: List[T_mo]
        '''
        здесь мы будем хранить фигуры да 7 шт,которые нужно сгенерировать.
        если он пуст,self.newPiece() пополнит его
        '''
        self.bag = [] # введите List[T_ShapeNames]

    def start(self):
        '''
        вызывается из родительского класса для начала новой игры
        '''
        self.isStarted = True
        self.waitForNextTimer = False
        self.completedLines = 0
        self.clearBoard()
        self.NewStatus.emit(str(self.completedLines))
        self.timer.start(Board.StartingSpeed, self)
        self.newPiece()

    def clearBoard(self):
        '''
        очищаем доску
        '''
        self.board = [NO_T_mo] * (Board.Rows * Board.Columns)

    def newPiece(self):
        '''
        получаем новую фигуру T_mo и размещаем ее на доске.если доска
        заполнена ,получаем :"игра окончена"
        '''
        if 0 == len(self.bag) :
            self.bag = make_bag()
        self.curPiece = T_mo( self.bag.pop() )

        self.curX = Board.Columns // 2 + 1
        self.curY = Board.Rows - 2 + self.curPiece.y_min()

        if not self.tryMove(self.curPiece, self.curX, self.curY):
            '''
            
            '''
            self.curPiece = NO_T_mo
            self.isStarted = False
            self.timer.stop()
            '''
            
            '''
            self.NewStatus.emit(
                "игра окончена, {} линий".format(self.completedLines)
                )
            self.update()

    def tryMove(self, newPiece, newX, newY) ->bool :
        '''
        Попробуем поместить активную фигуру в новую позицию. Этот метод
        вызывается, когда новая фигура создается впервые, и когда активная фигура
        вращается или перемещается.
        '''
        for i in range(4):

            x = newX + newPiece.x(i)
            y = newY + newPiece.y(i)
            if x < 0 or x >= Board.Columns:
                return False
            if y < 0 or y >= Board.Rows:
                return False

            if self.shapeAt(x, y) is not NO_T_mo:
                return False

        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()

        return True

    def keyPressEvent(self, event:QEvent):
        '''
        обрабатываем нажатие клавиш
        '''

        if self.isStarted and self.curPiece is not NO_T_mo :
            key = event.key()
            if key in self.validKeys :
                event.accept() #
                if key == Qt.Key_P:
                    self.togglePause()
                elif key == Qt.Key_Left:
                    self.tryMove(self.curPiece, self.curX - 1, self.curY)
                elif key == Qt.Key_Right:
                    self.tryMove(self.curPiece, self.curX + 1, self.curY)
                elif key == Qt.Key_Down:
                    self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)
                elif key == Qt.Key_Up:
                    self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)
                elif key == Qt.Key_Space:
                    self.dropDown()
                elif key == Qt.Key_D:
                    self.oneLineDown()
        if not event.isAccepted():
            ''' если мы на паузе ни один ключ не обрабатывается'''
            super().keyPressEvent(event)

    def togglePause(self):
        '''

        '''

        if not self.isStarted:
            return # игнорирует.когда не работает

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.NewStatus.emit("пауза")

        else:
            '''
            перезапускаем таймер
            '''
            self.timer.start(Board.StartingSpeed, self)
            self.NewStatus.emit(str(self.completedLines))

        self.update() # обновляем

    def timerEvent(self, event:QEvent):
        '''
        таймер истек. ждем очистку ряда и бросаем новую фигуру
        '''
        event.accept()
        if self.waitForNextTimer:
            self.waitForNextTimer = False
            self.newPiece()
        else:
            self.oneLineDown()

    def oneLineDown(self):
        '''

        '''
        if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
            self.pieceDropped()

    def dropDown(self):
        '''
        пробел == для быстрого опускания
        '''
        newY = self.curY
        while newY > 0:
            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break
            newY -= 1

        self.pieceDropped()

    def pieceDropped(self):
        '''
       если фигура подает и достигает последнего своего пристанища
       удаляем все полученные полные строки
        '''

        for (x,y) in self.curPiece.coords:
            self.setShapeAt(x+self.curX, y+self.curY, self.curPiece)

        self.removeFullLines()

        '''
        
        '''

    def setShapeAt(self, x:int, y:int, shape:T_mo):
        '''
        устанавливаем фигуру T_mo в ячейку доски
        '''
        self.board[(y * Board.Columns) + x] = shape
        #print('shape {} at x {} y {}'.format(shape.t_name,x,y))

    def shapeAt(self, x, y) -> T_mo :
        '''
        возвращает фигуру  T_mo в ячейку доски в х.у.
        '''
        return self.board[(y * Board.Columns) + x]

    def removeFullLines(self):
        '''

        '''

        '''
        состовляем список индексов полных строк.полный ряд --это 
        ряд который не содержит пустых ячеек,т.е.ссылок на  NO_ T_mo
        
        '''
        rowsToRemove = []
        for i in range(Board.Rows):
            n = 0
            for j in range(Board.Columns):
                if self.shapeAt(j, i) is not NO_T_mo:
                    n = n + 1

            if n == Board.Columns:
                rowsToRemove.append(i)
        '''
        
        '''
        rowsToRemove.reverse()

        '''
        
        '''
        for m in rowsToRemove:
            for k in range(m, Board.Rows-1):
                for l in range(Board.Columns):
                    self.setShapeAt(l, k, self.shapeAt(l, k + 1))

        '''
        обновляем строку ,и покажем количество удаленных строк
        '''
        self.completedLines += len(rowsToRemove)
        self.NewStatus.emit(str(self.completedLines))
        self.waitForNextTimer = True
        '''
        
        '''
        self.curPiece = NO_T_mo
        self.update()

    def paintEvent(self, event):
        '''

        '''
        painter = QPainter(self)
        rect = self.contentsRect()
        boardTop = rect.bottom() - Board.Rows * self.cellHeight()

        for i in range(Board.Rows):
            for j in range(Board.Columns):
                self.drawSquare(painter,
                                rect.left() + j * self.cellWidth(),
                                boardTop + i * self.cellHeight(),
                                self.shapeAt(j, Board.Rows - i - 1))

        if self.curPiece is not NO_T_mo:
            '''
           
            '''
            for i in range(4):
                x = self.curX + self.curPiece.x(i)
                y = self.curY + self.curPiece.y(i)
                self.drawSquare(painter,
                                rect.left() + x * self.cellWidth(),
                                boardTop + (Board.Rows - y - 1) * self.cellHeight(),
                                self.curPiece)

    def cellWidth(self) -> int :
        '''
        возвращаем ширину одной ячейки
        '''
        return self.contentsRect().width() // Board.Columns

    def cellHeight(self) -> int :
        '''
        возвращием высоту одной ячейки
        '''
        return self.contentsRect().height() // Board.Rows

    def drawSquare(self, painter:QPainter, x:int, y:int, shape:T_mo):
        '''

        '''
        color = shape.color()
        painter.fillRect(x + 1, y + 1, self.cellWidth() - 2,
            self.cellHeight() - 2, color)

        '''

        '''
        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.cellHeight() - 1, x, y)
        painter.drawLine(x, y, x + self.cellWidth() - 1, y)

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.cellHeight() - 1,
            x + self.cellWidth() - 1, y + self.cellHeight() - 1)
        painter.drawLine(x + self.cellWidth() - 1,
            y + self.cellHeight() - 1, x + self.cellWidth() - 1, y + 1)

'''
        делаем главное окно
'''

class Tetris(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Тетрис')
        '''
        создаем доску и делаем ее цетральным виджетом
        '''
        self.tboard = Board(self)
        self.setCentralWidget(self.tboard)
        '''
        Подключим сигнал обновления статуса к методу ShowMessage в строке состояния.
        '''
        self.tboard.NewStatus[str].connect(self.statusBar().showMessage)
        '''
        создаем геометрию главного окна
        '''
        self.resize(350, 550)
        self.center()
        '''
        начинаем игру
        '''
        self.tboard.start()
        self.show()

    def center(self):
        '''центрируем окно на экране'''

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2,
            (screen.height()-size.height())/2)

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
# выполняем командную строку

if __name__ == '__main__':

    import sys


    app = QApplication([])
    tetris = Tetris()
    tetris.show
    sys.exit(app.exec_())