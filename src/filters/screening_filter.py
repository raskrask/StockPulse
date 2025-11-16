from abc import ABC, abstractmethod
import xlrd

# フィルターの共通インターフェース
class ScreeningFilter(ABC):
    @abstractmethod
    def apply(self, book: xlrd.book.Book, candidates: list[int]) -> list[int]:
        pass
