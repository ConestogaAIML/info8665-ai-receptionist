"use client";

import { ListIcon } from "lucide-react";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { useFaqs } from "@/hooks/useFaqs";

interface FaqDrawerProps {
  businessId: number | null;
}

export function FaqDrawer({ businessId }: FaqDrawerProps) {
  const { faqs, isLoading, error } = useFaqs(businessId);
  const disabled = businessId === null;

  return (
    <Drawer direction="right">
      <DrawerTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2" disabled={disabled}>
          <ListIcon className="size-4" />
          View FAQs
        </Button>
      </DrawerTrigger>

      <DrawerContent className="sm:max-w-md">
        <DrawerHeader>
          <DrawerTitle>Business FAQs</DrawerTitle>
          <DrawerDescription>
            Reference questions and answers for MVP validation.
          </DrawerDescription>
        </DrawerHeader>

        <div className="flex min-h-0 flex-1 flex-col px-4 pb-4">
          {error && (
            <Alert variant="destructive" className="mb-3">
              <AlertDescription className="text-xs">{error}</AlertDescription>
            </Alert>
          )}

          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-20 w-full" />
              ))}
            </div>
          ) : faqs.length === 0 ? (
            <p className="text-sm text-muted-foreground">No FAQs found for this business.</p>
          ) : (
            <ScrollArea className="h-[calc(100vh-8rem)] pr-3">
              <ul className="space-y-4">
                {faqs.map((faq, index) => (
                  <li key={faq.id}>
                    <div className="space-y-2">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="text-sm font-medium leading-snug">{faq.question}</p>
                        {faq.category && (
                          <Badge variant="secondary" className="text-xs">
                            {faq.category}
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {faq.answer}
                      </p>
                    </div>
                    {index < faqs.length - 1 && <Separator className="mt-4" />}
                  </li>
                ))}
              </ul>
            </ScrollArea>
          )}
        </div>
      </DrawerContent>
    </Drawer>
  );
}
